INSERT INTO contacts
    (first_name, last_name, mechanisms, roles)
VALUES
    ('Leonardo', 'Davinci', '{ "(\"Email\",\"test@email.com\")" }', '{ "Science contact", "Metadata author" }');
INSERT INTO contacts
    (first_name, last_name)
VALUES
    ('Gregor', 'Mendel');
INSERT INTO atbds
    (title, alias)
VALUES
    ('Test ATBD 1', 'test-atbd-1');
INSERT INTO atbd_contacts
    (atbd_id, contact_id)
VALUES
    (1, 1);
INSERT INTO atbd_versions
    (atbd_id, atbd_version, scientific_theory, introduction, historical_perspective)
VALUES
    (1, 1,
        '{"document":{"nodes":[{"object":"block","type":"paragraph","nodes":[{"object":"text","leaves":[{"text":"A line of text in a paragraph."}]}]},
{"object":"block","type":"equation","nodes":[{"object":"text","leaves":[{"text":"\\int_0^\\infty x^2 dx"}]}]},
{"object":"block","type":"image","data":{"src":"http://localstack:4566/nasa-apt-dev-figures/fullmoon_resized.jpg", "caption": "Image of the full moon - 2019"}}]}}',
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"An introduction.","marks":[]}]}]},{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"","marks":[]}]}]},{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"","marks":[]}]}]},{"object":"block","type":"table","caption":"A Table containing important data", "data":{"headless":true},"nodes":[{"object":"block","type":"table_row","data":{},"nodes":[{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Table Column 1","marks":[{"object":"mark","type":"bold","data":{}}]}]}]}]},{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Table Column 2","marks":[{"object":"mark","type":"bold","data":{}}]}]}]}]},{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Table Column 3","marks":[{"object":"mark","type":"bold","data":{}}]}]}]}]}]},{"object":"block","type":"table_row","data":{},"nodes":[{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Cell value (short)","marks":[]}]}]}]},{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Cell value (long) - This is a super long cell value. It should be wrapped several times, perhaps 2 but although at this point maybe even 3. ","marks":[]}]}]}]},{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Cell value (short)","marks":[]}]}]}]}]},{"object":"block","type":"table_row","data":{},"nodes":[{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Cell value (short)","marks":[]}]}]}]},{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Cell value (short)","marks":[]}]}]}]},{"object":"block","type":"table_cell","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Cell value (short)","marks":[]}]}]}]}]}]},{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"","marks":[]}]}]}]}}',
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"A historical perspective. We are now referencing ","marks":[]}]},{"object":"inline","type":"reference","data":{"id":1,"name":"Example Reference"},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"ref","marks":[]}]}]},{"object":"text","leaves":[{"object":"leaf","text":"","marks":[]}]}]}]}}');
-- NOTE: the absolute url for fullmoon.jpg will work for the pdf serialization service running in docker-compose. it will not work for
-- web browser rendering same image. This can be manually changed to http://localhost:4566/nasa-apt-dev-figures/fullmoon.jpg
-- to render in browser.
INSERT INTO algorithm_input_variables
    (atbd_id, atbd_version, name, long_name)
VALUES
    (1, 1,
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Input Var 1","marks":[]}]}]}]}}',
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Input Variable 1","marks":[]}]}]}]}}');
INSERT INTO algorithm_input_variables
    (atbd_id, atbd_version, name, long_name, unit)
VALUES
    (1, 1,
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Input Var 2","marks":[]}]}]}]}}',
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Input variable that is quite long and should be wrapped over at least two lines but possible also three","marks":[]}]}]}]}}',
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Kelvins","marks":[]}]}]}]}}');
INSERT INTO algorithm_output_variables
    (atbd_id, atbd_version, name, long_name, unit)
VALUES
    (1, 1,
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Output Var 1","marks":[]}]}]}]}}',
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Output Variable 1","marks":[]}]}]}]}}',
        '{"object":"value","document":{"object":"document","data":{},"nodes":[{"object":"block","type":"paragraph","data":{},"nodes":[{"object":"text","leaves":[{"object":"leaf","text":"Kelvins","marks":[]}]}]}]}}');
INSERT INTO publication_references
    (publication_reference_id, atbd_version, atbd_id, authors, title, series, edition, volume, publication_place, publisher, pages, isbn, year)
VALUES
    (1, 1, 1, 'Charles Dickens,  John Steinbeck', 'Example Reference', 'A', '3rd', '42ml', 'Boston', 'Penguin Books', '189-198', 123456789, 1995);