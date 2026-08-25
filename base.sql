-- 🔴 PASO 1: Borrar primero las tablas que dependen de otras
DELETE FROM respuestas;
DELETE FROM resultados;
DELETE FROM preguntas;
DELETE FROM carreras;
DELETE FROM usuarios;
DELETE FROM areas_vocacionales;

-- 🔵 PASO 2: Restablecer los contadores (opcional, limpia los IDs)
ALTER TABLE areas_vocacionales AUTO_INCREMENT = 1;
ALTER TABLE carreras AUTO_INCREMENT = 1;
ALTER TABLE preguntas AUTO_INCREMENT = 1;

-- 🟢 PASO 3: Insertar las áreas nuevas
INSERT INTO areas_vocacionales (nombre, descripcion) VALUES
("Informática y Sistemas", "Desarrollo de software, redes, programación y tecnología"),
("Industria Alimentaria", "Producción, procesamiento y control de calidad de alimentos"),
("Mecánica Automotriz", "Mantenimiento, reparación y diseño de vehículos"),
("Electromecánica", "Instalación, mantenimiento de sistemas eléctricos y mecánicos");

-- 🟢 PASO 4: Insertar las carreras nuevas
INSERT INTO carreras (nombre, descripcion, area_id) VALUES
("Sistemas Informáticos", "Programación, bases de datos, redes y desarrollo de aplicaciones", 1),
("Industria de Alimentos", "Elaboración, conservación y control de calidad de productos alimenticios", 2),
("Mecánica Automotriz", "Diagnóstico, reparación y mantenimiento de motores y vehículos", 3),
("Electromecánica", "Sistemas eléctricos, máquinas, automatización e instalaciones industriales", 4);

-- 🟢 PASO 5: Insertar las preguntas nuevas
INSERT INTO preguntas (texto, area_id) VALUES
-- Sistemas Informáticos
("Me gusta descubrir cómo funcionan los programas y aplicaciones", 1),
("Disfruto aprendiendo sobre computadoras, redes y tecnología", 1),
("Me interesa crear o programar mis propias herramientas digitales", 1),
("Prefiero resolver problemas usando la lógica y herramientas informáticas", 1),
("Me atrae el mundo de internet, los sistemas y el tratamiento de información", 1),

-- Industria de Alimentos
("Me interesa saber cómo se elaboran y conservan los alimentos", 2),
("Me llama la atención el proceso de transformación de materias primas en productos", 2),
("Me gustaría trabajar controlando la calidad y seguridad de los alimentos", 2),
("Tengo curiosidad por conocer los procesos químicos y biológicos de los alimentos", 2),
("Me interesa la parte técnica de producción y procesamiento industrial", 2),

-- Mecánica Automotriz
("Me gusta desarmar y armar objetos para entender cómo funcionan", 3),
("Siento curiosidad por saber cómo funcionan los motores y los vehículos", 3),
("Prefiero trabajar con herramientas, piezas y máquinas físicas", 3),
("Me atrae diagnosticar fallas y reparar equipos y automóviles", 3),
("Me interesa aprender el funcionamiento de cada parte de un vehículo", 3),

-- Electromecánica
("Me interesa cómo funcionan la electricidad y los circuitos", 4),
("Disfruto entendiendo cómo se combinan sistemas eléctricos y mecánicos", 4),
("Me gustaría instalar y mantener equipos eléctricos e industriales", 4),
("Siento interés por las máquinas eléctricas, controles y automatización", 4),
("Me atrae trabajar con instalaciones, energía y tecnología industrial", 4);