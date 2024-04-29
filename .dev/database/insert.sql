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
('Task 2', 'This is task 2', '{"key": "value"}', 2);

-- Insert data into the prediction table
INSERT INTO prediction (model_name, model_version, result, score, task_id, project_id) VALUES
('Model 1', '1.0', '{"result": "value"}', 0.9, 1, 1),
('Model 2', '1.0', '{"result": "value"}', 0.8, 2, 2);

-- -- Insert data into the annotation table
-- INSERT INTO annotation (created_by, result, task_id, project_id) VALUES
-- (1, '{"result": "value"}', 1, 1),
-- (2, '{"result": "value"}', 1, 2);

-- -- Insert data into the user_task table
-- INSERT INTO user_task (id, task_id, task_status) VALUES
-- (1, 1, "in progress"),
-- (2, 1, "validated");
