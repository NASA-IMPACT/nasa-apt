INSERT INTO contacts(first_name, last_name, mechanisms, roles)
VALUES ('Leonardo', 'Davinci', '{ "(\"Email\",\"test@email.com\")" }', '{ "Science contact", "Metadata author" }');
INSERT INTO contacts(first_name, last_name)
VALUES ('Gregor', 'Mendel');
INSERT INTO atbds(title)
VALUES ('Test ATBD 1');
INSERT INTO atbd_contacts(atbd_id, contact_id)
VALUES (1, 1);
INSERT INTO atbd_versions(atbd_id, atbd_version, scientific_theory, introduction, historical_perspective)
VALUES (1, 1,
'{"document":{"nodes":[{"object":"block","type":"paragraph","nodes":[{"object":"text","leaves":[{"text":"A line of text in a paragraph."}]}]},
{"object":"block","type":"equation","nodes":[{"object":"text","leaves":[{"text":"\\int_0^\\infty x^2 dx"}]}]},
{"object":"block","type":"image","data":{"src":"http://localhost:4572/figures/fullmoon.jpg"}}]}}',
'{"document":{"nodes":[{"object":"block","type":"paragraph","nodes":[{"object":"text","leaves":[{"text":"An introduction."}]}]}]}}',
'{"document":{"nodes":[{"object":"block","type":"paragraph","nodes":[{"object":"text","leaves":[{"text":"A historical perspective."}]}]}]}}');
INSERT INTO algorithm_input_variables(atbd_id, atbd_version, name, long_name)
VALUES (1, 1, 'Input Var 1', 'Input variable 1');
INSERT INTO algorithm_output_variables(atbd_id, atbd_version, name, long_name)
VALUES (1, 1, 'Output Var 1', 'Output variable 1');