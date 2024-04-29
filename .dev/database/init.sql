

CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email text,
    role text,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "project" (
    id SERIAL PRIMARY KEY,
    title text,
    "description" text,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER REFERENCES "user" (id)
);

CREATE TABLE IF NOT EXISTS "task" (
    id SERIAL PRIMARY KEY,
    "name" text,
    instruction text,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    "data" json,
    project_id integer REFERENCES "project" (id)
);

CREATE TABLE IF NOT EXISTS "prediction" (
    id SERIAL PRIMARY KEY,
    model_name text,
    model_version text,
    result json,
    score float,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    task_id integer REFERENCES "task" (id),
    project_id integer REFERENCES "project" (id)
);

CREATE TABLE IF NOT EXISTS "annotation" (
    id SERIAL PRIMARY KEY,
    user_id integer REFERENCES "user" (id),
    result json,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    validated_at TIMESTAMP,
    task_id integer REFERENCES "task" (id),
    project_id integer REFERENCES "project" (id),
    "status" text DEFAULT 'in progress' 
);

CREATE TABLE IF NOT EXISTS "user_task" (
    user_id INTEGER REFERENCES "user" (id),
    task_status text,
    task_id INTEGER REFERENCES "task" (id),
    attributed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP,
    PRIMARY KEY (user_id)
);


-- Insert data into the user table
INSERT INTO "user" (email, role) VALUES 
('john@example.com', 'admin'),
('jane@example.com', 'user');

-- Insert data into the project table
INSERT INTO project (title, description, created_by) VALUES 
('Project 1', 'This is project 1', 1),
('Project 2', 'This is project 2', 2);

-- Insert data into the task table
INSERT INTO task (name, instruction, data, project_id) VALUES
('Task 1', 'This is task 1', '{"key": "value"}', 1),
('Test model v1', '10 segmentations à corriger pour evaluer la qualite du model', '{"key": "value"}', 1),
('Task 2', 'This is task 2', '{"key": "value"}', 2);

-- Insert data into the prediction table
INSERT INTO prediction (model_name, model_version, result, score, task_id, project_id) VALUES
('Model 1', '1.0', '{"result": "value"}', 0.9, 1, 1),
('Model 2', '1.0', '{"result": "value"}', 0.8, 2, 2);

-- Insert data into the annotation table
INSERT INTO annotation (user_id, result, task_id, project_id) VALUES
(1, '{"result": "value"}', 1, 1),
(2, '{"result": "value"}', 1, 2);

-- Insert data into the user_annotation table
INSERT INTO user_task (user_id, task_id, task_status) VALUES
(1, 1, 'in progress'),
(2, 1, 'validated');


UPDATE task
SET data = jsonb(pg_read_file('/docker-entrypoint-initdb.d/tasks.json'))
-- SET data = '{"key":"value","params":{"id":2,"opts":"true"}}'
WHERE name = 'Task 1';
