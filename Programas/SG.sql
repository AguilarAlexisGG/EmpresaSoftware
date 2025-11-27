CREATE DATABASE IF NOT EXISTS SG_Empresa;
USE SG_Empresa;

-- 1. Tabla Cliente
CREATE TABLE Cliente (
    id_cliente INT PRIMARY KEY AUTO_INCREMENT,
    nombre_cliente VARCHAR(100),
    correo VARCHAR(100),
    telefono VARCHAR(20),
    industria VARCHAR(50),
    pais VARCHAR(50),
    ciudad VARCHAR(50),
    nivel_satisfaccion INT -- Escala 1-5
);

-- 2. Tabla Metodología
CREATE TABLE Metodologia (
    id_metodologia INT PRIMARY KEY AUTO_INCREMENT,
    nombre_metodologia VARCHAR(100),
    documentacion TEXT
);

-- 3. Tabla Proyecto
CREATE TABLE Proyecto (
    id_proyecto INT PRIMARY KEY AUTO_INCREMENT,
    nombre_proyecto VARCHAR(100),
    id_cliente INT,
    fecha_inicio_estimada DATE,
    fecha_fin_estimada DATE,
    fecha_inicio_real DATE,
    fecha_fin_real DATE,
    estado ENUM('planificado', 'en curso', 'finalizado', 'cancelado'),
    presupuesto_estimado DECIMAL(12,2),
    presupuesto_real DECIMAL(12,2),
    valor_venta DECIMAL(12,2),
    ganancias DECIMAL(12,2),
    horas_estimadas INT,
    horas_totales INT,
    prioridad ENUM('alta', 'media', 'baja'),
    id_metodologia INT,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_metodologia) REFERENCES Metodologia(id_metodologia)
);

-- 4. Tabla Empleado
CREATE TABLE Empleado (
    id_empleado INT PRIMARY KEY AUTO_INCREMENT,
    nombre_completo VARCHAR(100),
    rol VARCHAR(50),
    salario_hora DECIMAL(10,2),
    disponibilidad BOOLEAN,
    fecha_contratacion DATE,
    estado_laboral ENUM('activo', 'inactivo'),
    habilidades TEXT
);

-- 5. Tabla Asignación Proyecto
CREATE TABLE AsignacionProyecto (
    id_asignacion INT PRIMARY KEY AUTO_INCREMENT,
    id_empleado INT,
    id_proyecto INT,
    rol VARCHAR(50),
    fecha_asignacion DATE,
    estado ENUM('activo', 'finalizado'),
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado),
    FOREIGN KEY (id_proyecto) REFERENCES Proyecto(id_proyecto)
);

-- 6. Tabla Tareas
CREATE TABLE Tarea (
    id_tarea INT PRIMARY KEY AUTO_INCREMENT,
    id_asignacion INT,
    nombre VARCHAR(100),
    fecha_asignacion DATE,
    fecha_limite DATE,
    estado ENUM('pendiente', 'en progreso', 'completada', 'bloqueada'),
    tiempo_estimado DECIMAL(5,2),
    tiempo_real DECIMAL(5,2),
    prioridad ENUM('alta', 'media', 'baja'),
    FOREIGN KEY (id_asignacion) REFERENCES AsignacionProyecto(id_asignacion)
);

-- 7. Tabla Pruebas (QA) - MEJORADA PARA DATOS DE CALIDAD
CREATE TABLE Prueba (
    id_prueba INT PRIMARY KEY AUTO_INCREMENT,
    id_asignacion INT, -- Tester responsable
    descripcion TEXT,
    tipo ENUM('unitaria', 'integración', 'aceptación', 'sistema'),
    fecha_ejecucion DATE,
    resultado ENUM('éxito', 'fallo', 'bloqueado'),
    -- Nuevo: Necesario para el análisis de riesgo y predicción
    severidad_defecto ENUM('nula', 'baja', 'media', 'alta', 'crítica'), 
    tiempo_resolucion_horas DECIMAL(5,2),
    FOREIGN KEY (id_asignacion) REFERENCES AsignacionProyecto(id_asignacion)
);

-- 8. Tabla Finanzas
CREATE TABLE Finanzas (
    id_finanza INT PRIMARY KEY AUTO_INCREMENT,
    id_proyecto INT,
    tipo_gasto ENUM('infraestructura', 'licencias', 'servicios', 'otros'),
    costo_estimado DECIMAL(12,2),
    costo_real DECIMAL(12,2),
    fecha_registro DATE,
    FOREIGN KEY (id_proyecto) REFERENCES Proyecto(id_proyecto)
);