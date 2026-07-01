from datetime import date
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, status
from scalar_fastapi import get_scalar_api_reference
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from payroll_api.database.connection import create_db_and_tables, get_async_session
from payroll_api.models.api_key import ApiKey
from payroll_api.models.api_key_country import ApiKeyCountry
from payroll_api.models.country import Country
from payroll_api.models.payroll_input import PayrollInput
from payroll_api.models.request_log import RequestLog
from payroll_api.models.rule_parameter import RuleParameter
from payroll_api.models.rule_parameter_version import RuleParameterVersion
from payroll_api.models.salary_rule import SalaryRule
from payroll_api.security import hash_api_key


@asynccontextmanager
async def lifespan(_: FastAPI):
	await create_db_and_tables()
	yield


app = FastAPI(title="Payroll API", lifespan=lifespan)


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
	return get_scalar_api_reference(
		openapi_url=app.openapi_url,
		title="Payroll API - Documentation",
	)

async def _resolve_country(session: AsyncSession, country: str) -> Country:
	country_code = country.upper()
	result = await session.exec(select(Country).where(Country.code == country_code))
	resolved_country = result.first()
	if resolved_country is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
	return resolved_country


async def _authorize(
	session: AsyncSession,
	country: str,
	x_api_key: str | None,
	x_api_user: str | None,
) -> tuple[ApiKey, Country]:
	if not x_api_key:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-API-Key header is required")
	if not x_api_user:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-API-User header is required")

	key_hash = hash_api_key(x_api_key)
	api_key_result = await session.exec(select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active.is_(True)))
	api_key = api_key_result.first()
	if api_key is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

	resolved_country = await _resolve_country(session, country)

	scope_result = await session.exec(
		select(ApiKeyCountry).where(
			ApiKeyCountry.api_key_id == api_key.id,
			ApiKeyCountry.country_id == resolved_country.id,
			ApiKeyCountry.is_active.is_(True),
		)
	)
	if scope_result.first() is None:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Country out of API key scope")

	return api_key, resolved_country


async def _log_request(
	session: AsyncSession,
	api_key_id: int | None,
	x_api_user: str | None,
	country_code: str,
	endpoint: str,
	method: str,
	status_code: int,
) -> None:
	request_log = RequestLog(
		api_key_id=api_key_id,
		api_key_user=x_api_user,
		country_code=country_code.upper(),
		endpoint=endpoint,
		method=method,
		status_code=status_code,
	)
	session.add(request_log)
	await session.commit()


def _salary_rule_to_dict(rule: SalaryRule) -> dict:
	return {
		"sequence": rule.sequence,
		"code": rule.code,
		"name": rule.name,
		"account_credit": rule.account_credit_code,
		"account_debit": rule.account_debit_code,
		"condition_select": rule.condition_select,
		"condition_python": rule.condition_python,
		"amount_select": rule.amount_select,
		"amount_python_compute": rule.amount_python_compute,
		"appears_on_payslip": rule.appears_on_payslip,
		"category_code": rule.category_code,
		"register_code": rule.register_code,
		"parent_rule_code": rule.parent_rule_code,
		"input_codes": rule.input_codes,
		"is_localization_rule": True,
	}


def _payroll_input_to_dict(payroll_input: PayrollInput) -> dict:
	return {
		"code": payroll_input.code,
		"name": payroll_input.name,
		"description": payroll_input.description,
		"input_type": payroll_input.input_type,
		"is_localization_rule": True,
	}


async def _get_salary_rule_list_for_country(session: AsyncSession, country_id: int) -> list[dict]:
	result = await session.exec(select(SalaryRule).where(SalaryRule.country_id == country_id, SalaryRule.is_active.is_(True)))
	rules = sorted(result.all(), key=lambda rule: rule.sequence)
	return [_salary_rule_to_dict(rule) for rule in rules]


async def _get_input_list_for_country(session: AsyncSession, country_id: int) -> list[dict]:
	result = await session.exec(select(PayrollInput).where(PayrollInput.country_id == country_id, PayrollInput.is_active.is_(True)))
	inputs = result.all()
	return [_payroll_input_to_dict(payroll_input) for payroll_input in inputs]


def _resolve_current_version(versions: list[RuleParameterVersion]) -> RuleParameterVersion | None:
	if not versions:
		return None

	today = date.today()
	valid_now = [
		version
		for version in versions
		if version.effective_from <= today and (version.effective_to is None or version.effective_to >= today)
	]
	if valid_now:
		return sorted(valid_now, key=lambda version: version.effective_from, reverse=True)[0]

	return sorted(versions, key=lambda version: version.effective_from, reverse=True)[0]


async def _get_rule_parameter_list_for_country(session: AsyncSession, country_id: int) -> list[dict]:
	parameter_result = await session.exec(
		select(RuleParameter).where(RuleParameter.country_id == country_id, RuleParameter.is_active.is_(True))
	)
	parameters = parameter_result.all()
	if not parameters:
		return []

	parameter_ids = [parameter.id for parameter in parameters if parameter.id is not None]
	version_result = await session.exec(
		select(RuleParameterVersion).where(
			RuleParameterVersion.rule_parameter_id.in_(parameter_ids),
			RuleParameterVersion.is_active.is_(True),
		)
	)
	versions = version_result.all()

	versions_by_parameter: dict[int, list[RuleParameterVersion]] = {}
	for version in versions:
		versions_by_parameter.setdefault(version.rule_parameter_id, []).append(version)

	result: list[dict] = []
	for parameter in parameters:
		parameter_versions = versions_by_parameter.get(parameter.id or -1, [])
		current_version = _resolve_current_version(parameter_versions)
		result.append(
			{
				"code": parameter.code,
				"name": parameter.name,
				"description": parameter.description,
				"data_type": parameter.data_type,
				"value": current_version.value if current_version else None,
				"effective_from": current_version.effective_from.isoformat() if current_version else None,
				"effective_to": current_version.effective_to.isoformat() if current_version and current_version.effective_to else None,
			}
		)

	return result


@app.get("/health")
async def health(session: AsyncSession = Depends(get_async_session)):
	result = await session.exec(select(1))
	db_status = result.one()

	return {
		"status": "ok",
		"database": "ok" if db_status == 1 else "error",
	}


@app.get("/v1/{country}/salary-rules")
async def get_salary_rule_list(
	country: str,
	session: AsyncSession = Depends(get_async_session),
	x_api_key: str | None = Header(None, alias="X-API-Key"),
	x_api_user: str | None = Header(None, alias="X-API-User"),
):
	api_key, resolved_country = await _authorize(session, country, x_api_key, x_api_user)
	response = await _get_salary_rule_list_for_country(session, resolved_country.id)

	await _log_request(session, api_key.id, x_api_user, resolved_country.code, "/v1/{country}/salary-rules", "GET", 200)
	return response


@app.get("/v1/{country}/salary-rules/{code}")
async def get_salary_rule(
	country: str,
	code: str,
	session: AsyncSession = Depends(get_async_session),
	x_api_key: str | None = Header(None, alias="X-API-Key"),
	x_api_user: str | None = Header(None, alias="X-API-User"),
):
	api_key, resolved_country = await _authorize(session, country, x_api_key, x_api_user)
	rules = await _get_salary_rule_list_for_country(session, resolved_country.id)
	selected_rule = next((rule for rule in rules if rule["code"] == code), None)
	if selected_rule is None:
		await _log_request(
			session,
			api_key.id,
			x_api_user,
			resolved_country.code,
			"/v1/{country}/salary-rules/{code}",
			"GET",
			404,
		)
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary rule not found")

	await _log_request(session, api_key.id, x_api_user, resolved_country.code, "/v1/{country}/salary-rules/{code}", "GET", 200)
	return selected_rule


@app.get("/v1/{country}/rule-parameters")
async def get_rule_parameter_list(
	country: str,
	session: AsyncSession = Depends(get_async_session),
	x_api_key: str | None = Header(None, alias="X-API-Key"),
	x_api_user: str | None = Header(None, alias="X-API-User"),
):
	api_key, resolved_country = await _authorize(session, country, x_api_key, x_api_user)
	response = await _get_rule_parameter_list_for_country(session, resolved_country.id)
	await _log_request(session, api_key.id, x_api_user, resolved_country.code, "/v1/{country}/rule-parameters", "GET", 200)
	return response


@app.get("/v1/{country}/rule-parameters/{code}")
async def get_rule_parameter(
	country: str,
	code: str,
	session: AsyncSession = Depends(get_async_session),
	x_api_key: str | None = Header(None, alias="X-API-Key"),
	x_api_user: str | None = Header(None, alias="X-API-User"),
):
	api_key, resolved_country = await _authorize(session, country, x_api_key, x_api_user)
	parameters = await _get_rule_parameter_list_for_country(session, resolved_country.id)
	selected_parameter = next((parameter for parameter in parameters if parameter["code"] == code), None)
	if selected_parameter is None:
		await _log_request(
			session,
			api_key.id,
			x_api_user,
			resolved_country.code,
			"/v1/{country}/rule-parameters/{code}",
			"GET",
			404,
		)
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule parameter not found")

	await _log_request(session, api_key.id, x_api_user, resolved_country.code, "/v1/{country}/rule-parameters/{code}", "GET", 200)
	return selected_parameter


@app.get("/v1/{country}/inputs")
async def get_input_list(
	country: str,
	session: AsyncSession = Depends(get_async_session),
	x_api_key: str | None = Header(None, alias="X-API-Key"),
	x_api_user: str | None = Header(None, alias="X-API-User"),
):
	api_key, resolved_country = await _authorize(session, country, x_api_key, x_api_user)
	response = await _get_input_list_for_country(session, resolved_country.id)
	await _log_request(session, api_key.id, x_api_user, resolved_country.code, "/v1/{country}/inputs", "GET", 200)
	return response


@app.get("/v1/{country}/inputs/{code}")
async def get_input(
	country: str,
	code: str,
	session: AsyncSession = Depends(get_async_session),
	x_api_key: str | None = Header(None, alias="X-API-Key"),
	x_api_user: str | None = Header(None, alias="X-API-User"),
):
	api_key, resolved_country = await _authorize(session, country, x_api_key, x_api_user)
	inputs = await _get_input_list_for_country(session, resolved_country.id)
	selected_input = next((input_item for input_item in inputs if input_item["code"] == code), None)
	if selected_input is None:
		await _log_request(
			session,
			api_key.id,
			x_api_user,
			resolved_country.code,
			"/v1/{country}/inputs/{code}",
			"GET",
			404,
		)
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Input not found")

	await _log_request(session, api_key.id, x_api_user, resolved_country.code, "/v1/{country}/inputs/{code}", "GET", 200)
	return selected_input