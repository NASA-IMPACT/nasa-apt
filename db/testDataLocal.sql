INSERT INTO contacts
    (first_name, last_name, mechanisms, roles)
SELECT 'Leonardo', 'Davinci', '{ "(\"Email\",\"test@email.com\")" }', '{ "Science contact", "Metadata author" }'
WHERE 
    NOT EXISTS(
        SELECT first_name, last_name, mechanisms, roles
FROM contacts
WHERE first_name = 'Leonardo' AND last_name = 'Davinci'
    );
INSERT INTO contacts
    (first_name, last_name)
SELECT 'Gregor', 'Mendel'
WHERE 
    NOT EXISTS(
        SELECT first_name, last_name
FROM contacts
WHERE first_name = 'Gregor' AND last_name = 'Mendel'
    );
INSERT INTO atbds
    (title, alias, created_by)
VALUES
    ('Test ATBD 1', 'test-atbd-1', 'LeoThomas123');

INSERT INTO atbd_versions
    (atbd_id, created_by, major, minor, document, status)
VALUES
    (1, 'LeoThomas123', 1, 0, '{
    "scientific_theory": {
        "document": {
            "nodes": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "text": "A line of text in a paragraph."
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "equation",
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "text": "\\int_0^\\infty x^2 dx"
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "image",
                    "data": {
                        "src": "fullmoon.jpg",
                        "caption": "Image of the full moon - 2019"
                    }
                }
            ]
        }
    },
    "introduction": {
        "object": "value",
        "document": {
            "object": "document",
            "data": {},
            "nodes": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "An introduction.",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "table",
                    "caption": "A Table containing important data",
                    "data": {
                        "headless": true
                    },
                    "nodes": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Table Column 1",
                                                            "marks": [
                                                                {
                                                                    "object": "mark",
                                                                    "type": "bold",
                                                                    "data": {}
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Table Column 2",
                                                            "marks": [
                                                                {
                                                                    "object": "mark",
                                                                    "type": "bold",
                                                                    "data": {}
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Table Column 3",
                                                            "marks": [
                                                                {
                                                                    "object": "mark",
                                                                    "type": "bold",
                                                                    "data": {}
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (long) - This is a super long cell value. It should be wrapped several times, perhaps 2 but although at this point maybe even 3. ",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "historical_perspective": {
        "object": "value",
        "document": {
            "object": "document",
            "data": {},
            "nodes": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "A historical perspective. We are now referencing ",
                                    "marks": []
                                }
                            ]
                        },
                        {
                            "object": "inline",
                            "type": "reference",
                            "data": {
                                "id": 1,
                                "name": "Example Reference"
                            },
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "ref",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "algorithm_input_variables": [
        {
            "name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input Var 1",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            "long_name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input Variable 1",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        },
        {
            "name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input Var 2",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            "long_name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input variable that is quite long and should be wrapped over at least two lines but possible also three",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            "unit": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Kelvins",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
    ],
    "algorithm_output_variables": [{
        "name": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "Output Var 1",
                                        "marks": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        },
        "long_name": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "Output Variable 1",
                                        "marks": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        },
        "unit": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "Kelvins",
                                        "marks": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }],
    "publication_references": [
        {
            "publication_reference_id": 1,
            "authors": "Charles Dickens,  John Steinbeck",
            "title": "Example Reference",
            "series": "A",
            "edition": "3rd",
            "volume": "42ml",
            "issue":"ticket",
            "publication_place": "Boston",
            "publisher": "PenguinBooks",
            "pages": "189-198",
            "isbn": 123456789,
            "year": 1996
        }
    ]
}',
        'Published');

INSERT INTO atbd_versions
    (atbd_id, created_by, major, minor, document)
VALUES
    (1, 'LeoThomas123', 2, 0, '{
    "scientific_theory": {
        "document": {
            "nodes": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "text": "A line of text in a paragraph."
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "equation",
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "text": "\\int_0^\\infty x^2 dx"
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "image",
                    "data": {
                        "src": "fullmoon.jpg",
                        "caption": "Image of the full moon - 2019"
                    }
                }
            ]
        }
    },
    "introduction": {
        "object": "value",
        "document": {
            "object": "document",
            "data": {},
            "nodes": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "An introduction.",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "table",
                    "caption": "A Table containing important data",
                    "data": {
                        "headless": true
                    },
                    "nodes": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Table Column 1",
                                                            "marks": [
                                                                {
                                                                    "object": "mark",
                                                                    "type": "bold",
                                                                    "data": {}
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Table Column 2",
                                                            "marks": [
                                                                {
                                                                    "object": "mark",
                                                                    "type": "bold",
                                                                    "data": {}
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Table Column 3",
                                                            "marks": [
                                                                {
                                                                    "object": "mark",
                                                                    "type": "bold",
                                                                    "data": {}
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (long) - This is a super long cell value. It should be wrapped several times, perhaps 2 but although at this point maybe even 3. ",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "object": "block",
                            "type": "table_row",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "object": "block",
                                    "type": "table_cell",
                                    "data": {},
                                    "nodes": [
                                        {
                                            "object": "block",
                                            "type": "paragraph",
                                            "data": {},
                                            "nodes": [
                                                {
                                                    "object": "text",
                                                    "leaves": [
                                                        {
                                                            "object": "leaf",
                                                            "text": "Cell value (short)",
                                                            "marks": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "historical_perspective": {
        "object": "value",
        "document": {
            "object": "document",
            "data": {},
            "nodes": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "data": {},
                    "nodes": [
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "A historical perspective. We are now referencing ",
                                    "marks": []
                                }
                            ]
                        },
                        {
                            "object": "inline",
                            "type": "reference",
                            "data": {
                                "id": 1,
                                "name": "Example Reference"
                            },
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "ref",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "object": "text",
                            "leaves": [
                                {
                                    "object": "leaf",
                                    "text": "",
                                    "marks": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    },
    "algorithm_input_variables": [
        {
            "name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input Var 1",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            "long_name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input Variable 1",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        },
        {
            "name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input Var 2",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            "long_name": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Input variable that is quite long and should be wrapped over at least two lines but possible also three",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            "unit": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "data": {},
                            "nodes": [
                                {
                                    "object": "text",
                                    "leaves": [
                                        {
                                            "object": "leaf",
                                            "text": "Kelvins",
                                            "marks": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
    ],
    "algorithm_output_variables":[ {
        "name": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "Output Var 1",
                                        "marks": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        },
        "long_name": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "Output Variable 1",
                                        "marks": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        },
        "unit": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "Kelvins",
                                        "marks": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }],
    "publication_references": [
        {
            "publication_reference_id": 1,
            "authors": "Charles Dickens,  John Steinbeck",
            "title": "Example Reference",
            "series": "A",
            "edition": "3rd",
            "volume": "42ml",
            "publication_place": "Boston",
            "issue": "ticket",
            "publisher": "PenguinBooks",
            "pages": "189-198",
            "isbn": 123456789,
            "year": 1995
        }
    ]
}');
        