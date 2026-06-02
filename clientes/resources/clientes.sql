
drop table if exists clientes;

CREATE TABLE cliente(  
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    cedula VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL
);