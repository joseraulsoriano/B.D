CREATE DATABASE sistema_eventos;
USE sistema_eventos;

-- Tabla Usuario
CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidoP VARCHAR(50) NOT NULL,
    apellidoM VARCHAR(50),
    género ENUM('Masculino', 'Femenino', 'Otro') NOT NULL,
    fecha_nac DATE NOT NULL,
    nacionalidad VARCHAR(50) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    tipo_contrato VARCHAR(50),
    rol ENUM('Participante', 'Instructor', 'Responsable') NOT NULL
);

-- Tabla para atributo multivalorado Nombre
CREATE TABLE Nombre (
    id_nombre INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    PNombre VARCHAR(50) NOT NULL,
    SNombre VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Tabla Participante
CREATE TABLE Participante (
    id_participante INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    procedencia VARCHAR(100),
    id_usuario INT UNIQUE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Tabla para atributo multivalorado Procedencia
CREATE TABLE Procedencia (
    id_procedencia INT AUTO_INCREMENT PRIMARY KEY,
    id_participante INT NOT NULL,
    pais VARCHAR(50) NOT NULL,
    estado VARCHAR(50),
    municipio VARCHAR(50),
    colonia VARCHAR(50),
    FOREIGN KEY (id_participante) REFERENCES Participante(id_participante) ON DELETE CASCADE
);

-- Tabla Instructor
CREATE TABLE Instructor (
    id_instructor INT AUTO_INCREMENT PRIMARY KEY,
    CV TEXT,
    id_usuario INT UNIQUE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Tabla Responsable
CREATE TABLE Responsable (
    id_responsable INT AUTO_INCREMENT PRIMARY KEY,
    área VARCHAR(50) NOT NULL,
    id_usuario INT UNIQUE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Tabla Validación
CREATE TABLE Validacion (
    id_validacion INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    comentarios TEXT,
    estado VARCHAR(20) NOT NULL
);

-- Tabla ODS
CREATE TABLE ODS (
    id_ods INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla Organización
CREATE TABLE Organizacion (
    id_organizacion INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    origen VARCHAR(50) NOT NULL
);

-- Tabla Tematica
CREATE TABLE Tematica (
    id_tematica INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla Evento
CREATE TABLE Evento (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    modalidad ENUM('Presencial', 'Virtual', 'Híbrido') NOT NULL,
    tipo_entrega VARCHAR(50),
    descripcion TEXT,
    num_registro VARCHAR(50) UNIQUE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado VARCHAR(20) NOT NULL,
    periodo_academico VARCHAR(50),
    microcredencial BOOLEAN DEFAULT FALSE,
    duracion_horas INT NOT NULL,
    costo_Participante DECIMAL(10,2),
    id_tematica INT,
    FOREIGN KEY (id_tematica) REFERENCES Tematica(id_tematica)
);

-- Tabla FinanzaEvento (relación 1:1 con Evento)
CREATE TABLE FinanzaEvento (
    id_finanza INT AUTO_INCREMENT PRIMARY KEY,
    porcentaje_ingreso DECIMAL(5,2),
    fee_aportado DECIMAL(10,2),
    id_evento INT UNIQUE NOT NULL,
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento) ON DELETE CASCADE
);

-- Tabla intermedia Evento_ODS (relación N:M)
CREATE TABLE Evento_ODS (
    id_evento INT NOT NULL,
    id_ods INT NOT NULL,
    PRIMARY KEY (id_evento, id_ods),
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_ods) REFERENCES ODS(id_ods) ON DELETE CASCADE
);

-- Tabla intermedia Evento_Participante (relación N:M)
CREATE TABLE Evento_Participante (
    id_evento INT NOT NULL,
    id_participante INT NOT NULL,
    Asistencia BOOLEAN DEFAULT FALSE,
    fecha_registro DATE NOT NULL,
    constancia_creada BOOLEAN DEFAULT FALSE,
    evaluacion_programada BOOLEAN DEFAULT FALSE,
    evaluacion_profesores BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id_evento, id_participante),
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_participante) REFERENCES Participante(id_participante) ON DELETE CASCADE
);

-- Tabla intermedia Evento_Responsable (relación N:M)
CREATE TABLE Evento_Responsable (
    id_evento INT NOT NULL,
    id_responsable INT NOT NULL,
    PRIMARY KEY (id_evento, id_responsable),
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_responsable) REFERENCES Responsable(id_responsable) ON DELETE CASCADE
);

-- Tabla intermedia Evento_Instructor (relación N:M)
CREATE TABLE Evento_Instructor (
    id_evento INT NOT NULL,
    id_instructor INT NOT NULL,
    pagoInstructor DECIMAL(10,2),
    PRIMARY KEY (id_evento, id_instructor),
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_instructor) REFERENCES Instructor(id_instructor) ON DELETE CASCADE
);

-- Tabla intermedia Evento_Organizacion (relación N:M)
CREATE TABLE Evento_Organizacion (
    id_evento INT NOT NULL,
    id_organizacion INT NOT NULL,
    PRIMARY KEY (id_evento, id_organizacion),
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_organizacion) REFERENCES Organizacion(id_organizacion) ON DELETE CASCADE
);

-- Tabla intermedia Validacion_Responsable (relación N:M)
CREATE TABLE Validacion_Responsable (
    id_responsable INT NOT NULL,
    id_validacion INT NOT NULL,
    PRIMARY KEY (id_responsable, id_validacion),
    FOREIGN KEY (id_responsable) REFERENCES Responsable(id_responsable) ON DELETE CASCADE,
    FOREIGN KEY (id_validacion) REFERENCES Validacion(id_validacion) ON DELETE CASCADE
);