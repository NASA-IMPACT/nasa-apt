INSERT INTO contacts (first_name, last_name, mechanisms)
-- SELECT 'Leonardo', 'Davinci', '{ "(\"Email\",\"test@email.com\")" }'
SELECT
  'Leonardo',
  'Davinci',
  ARRAY[ROW ('Email', 'test@email.com'), ROW ('Twitter', '@test_handle')]::contact_mechanism[]
WHERE
  NOT EXISTS (
    SELECT
      first_name,
      last_name,
      mechanisms
    FROM
      contacts
    WHERE
      first_name = 'Leonardo'
      AND last_name = 'Davinci');

INSERT INTO contacts (first_name, last_name, mechanisms)
-- SELECT 'Gregor', 'Mendel', '{ "(\"Mobile\", \"1 (234) 567 - 8910\")" }'
SELECT
  'Gregor',
  'Mendel',
  ARRAY[ROW ('Mobile', '1(234)567-8910')]::contact_mechanism[]
WHERE
  NOT EXISTS (
    SELECT
      first_name,
      last_name,
      mechanisms
    FROM
      contacts
    WHERE
      first_name = 'Gregor'
      AND last_name = 'Mendel');

INSERT INTO atbds (title, alias, created_by, last_updated_by)
  VALUES ('Test ATBD 1', 'test-atbd-1', :'owner_sub', :'owner_sub');

INSERT INTO atbd_versions (atbd_id, created_by, "owner", authors, reviewers, last_updated_by, published_by, major, minor, document, citation, status)
  VALUES (1, :'owner_sub', :'owner_sub', ARRAY[:'author_sub_1', :'author_sub_2']::text[], ARRAY[jsonb_object(ARRAY['sub', :'reviewer_sub_1', 'review_status', 'IN_PROGRESS']::text[]), jsonb_object(ARRAY['sub', :'reviewer_sub_2', 'review_status', 'IN_PROGRESS']::text[])]::jsonb[], :'author_sub_1', :'curator_sub', 1, 1, '{
  "abstract": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "This is the super duper document abstract "
          }
        ]
      } 
    ] 
  },
  "version_description": {
    "children":[
      {
        "type": "p",
        "children":[
          {
            "text": "The important aspects of this document version include updated handling of the flux capcitor and addition of a description of the impulse response of an inhomogeneous linear differential operator defined on a domain with specified initial conditions or boundary conditions, also known as Green''s function:"
          }
        ]
      },
      {
        "type": "equation",
        "children": [
          {"text": "\\int_C P\\,du + Q\\, dv = \\int\\!\\!\\!\\int_A \\left({\\partial Q\\over \\partial u} - {\\partial P\\over \\partial v}\\right) {1\\over \\sqrt{EG-F^2}}\\,dA"}
        ]
      }
    ]
  },
  "introduction": null,
  "historical_perspective": null,
  "additional_information": null,
  "data_availability":null,
  "mathematical_theory": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "The algorithm specified in this document is designed to derive footprint level canopy cover and vertical "
          },
          {
            "type": "a",
            "url": "https://en.wikipedia.org/",
            "children": [
              {
                "text": "profile over vegetated areas"
              }
            ]
          },
          {
            "text": " between ~52°N and ~52°S.\nThe data product includes estimates of total canopy cover and PAI, vertical profiles of canopy cover and PAI, the vertical profile of Plant Area Volume Density and foliage height diversity. The GEDI Level 2A and 2B products will provide unprecedented dense spatial samplings of forest structure globally."
          }
        ]
      },
      {
        "type": "p",
        "children": [
          {
            "text": "Canopy cover is a biophysical parameter widely used in terrestrial remote sensing to describe the spatially aggregated geometric properties of vegetation. Multiple definitions of canopy cover exist, depending on the applied measuring techniques."
          }
        ]
      },
      {
        "type": "p",
        "children": [
          {
            "text": "The central issues in the definition are:"
          }
        ]
      },
      {
        "type": "ol",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether the measurement is acquired at a specific viewing angle (mostly near-nadir) or over the entire hemisphere;"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether a tree crown is treated as an opaque object including all small within-canopy gaps."
                  }, 
                  {
                    "text": "This text demonstrates "
                  }, 
                  {
                    "text": "subscripted", 
                    "subscript": true
                  },
                  {
                    "text": "text, as well as " 
                  },
                  {
                    "text": "underlined", 
                    "underline": true
                  }, 
                  {
                    "text": "text"
                  }
                ]
              }
            ]
          }, 
          {
            "type": "li",
            "children": [
              {
                "type": "ul",
                "children": [
                  {
                    "type":"li",
                    "children":[ {"type":"p", "children": [{"text": "This is an example"} ]}]
                  },
                  {
                    "type":"li",
                    "children":[ {"type":"p", "children": [{"text": "Of a list within a list!"} ]}]
                  },
                  {
                    "type":"li",
                    "children":[ {"type":"p", "children": [{"text": "Pretty neat, no?!"} ]}]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "mathematical_theory_assumptions": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "There are no assumptions being made "
          },
          {
            "text": "at the moment",
            "italic": true
          },
          {
            "text": "."
          }
        ]
      }
    ]
  },
  "algorithm_input_variables": [],
  "algorithm_input_variables_caption": null,
  "algorithm_output_variables": [
    {
      "name": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "Acc"
              }
            ]
          }
        ]
      },
      "long_name": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "Acceleration"
              }
            ]
          }
        ]
      },
      "unit": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "m/s"
              },
              {
                "text": "2",
                "superscript": true
              }
            ]
          }
        ]
      }
    }
  ],
  "algorithm_output_variables_caption": "This is a caption for algorithm output variables",
  "algorithm_usage_constraints": null,
  "performance_assessment_validation_methods": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "Some methods were taken to test this:"
          }
        ]
      },
      {
        "type": "ol",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "Creating lists"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "and that is all folks"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "performance_assessment_validation_uncertainties": null,
  "performance_assessment_validation_errors": null ,
  "algorithm_implementations": [
    {
      "url": "https://developmentseed.org/",
      "description": "This is our website"
    }
  ],
  "data_access_input_data": [],
  "data_access_output_data": [
    {
      "url": "https://youtube.com",
      "description": "This is basically a link to youtube"
    }
  ],
  "data_access_related_urls": [],
  "journal_discussion": null,
  "journal_acknowledgements": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "Thank you to all that are testing this tool! "
          },
          {
            "text": "You are the best!",
            "bold": true
          }
        ]
      }
    ]
  },
  "scientific_theory": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "The "
          },
          {
            "text": "algorithm",
            "bold": true
          },
          {
            "text": " specified in this "
          },
          {
            "text": "document",
            "bold": true,
            "italic": true
          },
          {
            "type": "ref",
            "refId": "1",
            "children": [
              {
                "text": ""
              }
            ]
          },
          {
            "text": " is designed to derive footprint level canopy cover and vertical "
          },
          {
            "type": "a",
            "url": "https://en.wikipedia.org",
            "children": [
              {
                "text": "profile over vegetated areas"
              }
            ]
          },
          {
            "text": " between ~52°N and ~52°S.\nThe data product includes estimates of total canopy cover and PAI."
          }
        ]
      },
      {
        "type": "p",
        "children": [
          {
            "text": "The central "
          },
          {
            "text": "issues",
            "superscript": true
          },
          {
            "text": " in the definition are:"
          }
        ]
      },
      {
        "type": "ol",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether the measurement is acquired at a specific viewing angle (mostly near-nadir) or over the entire hemisphere;"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether a tree crown is treated as an opaque object including all small within-canopy gaps."
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Equation Example"
          }
        ], 
        "id": "equation-example"
      },
      {
        "type": "equation",
        "children": [
          {
            "text": "F_{app}(x) = \\sum_{n=1}^{\\infty} \\sqrt {2^{-n} \\cdot x}"
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Image Example"
          }
        ],
        "id":"image-example"
      },
      {
        "type": "image-block",
        "children": [
          { 
            "type": "img",
            "objectKey": "fullmoon.jpg",
            "children": [ {"text": ""}]
          },
          {
            "type": "caption",
            "children": [ {"text": "This is an image caption"}]
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Table Example"
          }
        ],
        "id":"table-example"
      },
      {
        "type": "table-block",
        "children": [
          {
            "type": "table",
            "children": [
              {
                "type": "tr",
                "children": [
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Name",
                            "bold": true
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Result",
                            "bold": true
                          }
                        ]
                      }
                    ]
                  }, 
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Date",
                            "bold": true
                          }
                        ]
                      }
                    ]
                  }
                ]
              },
              {
                "type": "tr",
                "children": [
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Lincoln"
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Inconclusive"
                          }
                        ]
                      }
                    ]
                  }, 
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "2020-01-01 at 00:00:00"
                          }
                        ]
                      }
                    ]
                  }
                ]
              },
              {
                "type": "tr",
                "children": [
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Bridge-water"
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Pass"
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "2020-01-01 at 00:00:00"
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
            "type": "caption",
            "children": [
              {
                "text": "Test results by "
              },
              {
                "type": "a",
                "url": "http://google.com",
                "children": [
                  {
                    "text": "different"
                  }
                ]
              },
              {
                "text": " entities"
              }
            ]
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Canopy cover types"
          }
        ],
        "id":"canopy-cover-types"
      },
      {
        "type": "p",
        "children": [
          {
            "text": "It is different from two other widely used cover types: "
          }
        ]
      },
      {
        "type": "ul",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "canopy closure defined as the proportion of the vegetation over a segment of the sky hemisphere at one point on the ground"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "crown cover as the percentage of the ground covered by a vertical projection of the outermost perimeter of the natural spread of the foliage of plants."
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "scientific_theory_assumptions": null,
  "publication_references": [
    {
      "id": "1",
      "authors": "Dickens, Charles and Steinbeck, John",
      "title": "Example Reference",
      "series": "A",
      "edition": "3rd",
      "volume": "42ml",
      "issue": "ticket",
      "publication_place": "Boston",
      "publisher": "PenguinBooks",
      "pages": "189-198",
      "isbn": "123456789",
      "year": "1995"
    }
  ]
}'::jsonb, '{
  "creators": "Leo Thomas and Daniel da Silva and Ricardo Mestre",
  "editors": "Olaf Veerman",
  "title": "A full atbd for testing",
  "series_name": "Tests of content",
  "release_date": "2021-01-01",
  "release_place": "World Wide Web",
  "publisher": "Development Seed",
  "version": "2",
  "issue": "alpha2",
  "additional_details": "",
  "online_resource": "http://nasa-apt2-staging.s3-website-us-east-1.amazonaws.com/"
}'::jsonb, 'PUBLISHED');

INSERT INTO atbd_versions (atbd_id, created_by, "owner", authors, reviewers, last_updated_by, major, minor, document, citation, status)
  VALUES (1, :'owner_sub', :'owner_sub', ARRAY[:'author_sub_1', :'author_sub_2']::text[], ARRAY[jsonb_object(ARRAY['sub', :'reviewer_sub_1', 'review_status', 'IN_PROGRESS']::text[]), jsonb_object(ARRAY['sub', :'reviewer_sub_2', 'review_status', 'IN_PROGRESS']::text[])]::jsonb[], :'author_sub_1', 2, 0, '{
  "abstract": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "The algorithm specified in this document is designed to derive footprint level canopy cover and vertical "
          }
        ]
      } 
    ] 
  },
  "version_description": {
    "children":[
      {
        "type": "p",
        "children":[
          {
            "text": "The important aspects of this document version include updated handling of the flux capcitor and addition of a description of the impulse response of an inhomogeneous linear differential operator defined on a domain with specified initial conditions or boundary conditions, also known as Green''s function:"
          }
        ]
      },
      {
        "type": "equation",
        "children": [
          {"text": "\\int_C P\\,du + Q\\, dv = \\int\\!\\!\\!\\int_A \\left({\\partial Q\\over \\partial u} - {\\partial P\\over \\partial v}\\right) {1\\over \\sqrt{EG-F^2}}\\,dA" }
        ]
      }
    ]
  },
  "introduction": null,
  "historical_perspective": null,
  "additional_information": null,
  "data_availability":null,
  "mathematical_theory": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "The algorithm specified in this document is designed to derive footprint level canopy cover and vertical "
          },
          {
            "type": "a",
            "url": "https://en.wikipedia.org/",
            "children": [
              {
                "text": "profile over vegetated areas"
              }
            ]
          },
          {
            "text": " between ~52°N and ~52°S.\nThe data product includes estimates of total canopy cover and PAI, vertical profiles of canopy cover and PAI, the vertical profile of Plant Area Volume Density and foliage height diversity. The GEDI Level 2A and 2B products will provide unprecedented dense spatial samplings of forest structure globally."
          }
        ]
      },
      {
        "type": "p",
        "children": [
          {
            "text": "Canopy cover is a biophysical parameter widely used in terrestrial remote sensing to describe the spatially aggregated geometric properties of vegetation. Multiple definitions of canopy cover exist, depending on the applied measuring techniques."
          }
        ]
      },
      {
        "type": "p",
        "children": [
          {
            "text": "The central issues in the definition are:"
          }
        ]
      },
      {
        "type": "ol",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether the measurement is acquired at a specific viewing angle (mostly near-nadir) or over the entire hemisphere;"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether a tree crown is treated as an opaque object including all small within-canopy gaps."
                  }, 
                  {
                    "text": "This text demonstrates "
                  }, 
                  {
                    "text": "subscripted", 
                    "subscript": true
                  },
                  {
                    "text": "text, as well as " 
                  },
                  {
                    "text": "underlined", 
                    "underline": true
                  }, 
                  {
                    "text": "text"
                  }
                ]
              }
            ]
          }, 
          {
            "type": "li",
            "children": [
              {
                "type": "ul",
                "children": [
                  {
                    "type":"li",
                    "children":[ {"type":"p", "children": [{"text": "This is an example"} ]}]
                  },
                  {
                    "type":"li",
                    "children":[ {"type":"p", "children": [{"text": "Of a list within a list!"} ]}]
                  },
                  {
                    "type":"li",
                    "children":[ {"type":"p", "children": [{"text": "Pretty neat, no?!"} ]}]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "mathematical_theory_assumptions": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "There are no assumptions being made "
          },
          {
            "text": "at the moment",
            "italic": true
          },
          {
            "text": "."
          }
        ]
      }
    ]
  },
  "algorithm_input_variables": [],
  "algorithm_input_variables_caption": null,
  "algorithm_output_variables": [
    {
      "name": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "Acc"
              }
            ]
          }
        ]
      },
      "long_name": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "Acceleration"
              }
            ]
          }
        ]
      },
      "unit": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "m/s"
              },
              {
                "text": "2",
                "superscript": true
              }
            ]
          }
        ]
      }
    }
  ],
  "algorithm_output_variables_caption": "Algorithm Variables table caption :)",
  "algorithm_usage_constraints": null,
  "performance_assessment_validation_methods": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "Some methods were taken to test this:"
          }
        ]
      },
      {
        "type": "ol",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "Creating lists"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "and that is all folks"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "performance_assessment_validation_uncertainties": null,
  "performance_assessment_validation_errors": null,
  "algorithm_implementations": [
    {
      "url": "https://developmentseed.org/this-is-a-verylongwebsiteurl?with=parameters&that=aresuperlong-and-have-hyphens&123=4567891011121314151617181920",
      "description": "This is our website"
    }
  ],
  "data_access_input_data": [],
  "data_access_output_data": [
    {
      "url": "https://youtube.com",
      "description": "This is basically a link to youtube"
    }
  ],
  "data_access_related_urls": [],
  "journal_discussion": null,
  "journal_acknowledgements": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "Thank you to all that are testing this tool! "
          },
          {
            "text": "You are the best!",
            "bold": true
          }
        ]
      }
    ]
  },
  "scientific_theory": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "The "
          },
          {
            "text": "algorithm",
            "bold": true
          },
          {
            "text": " specified in this "
          },
          {
            "text": "document",
            "bold": true,
            "italic": true
          },
          {
            "type": "ref",
            "refId": "1",
            "children": [
              {
                "text": ""
              }
            ]
          },
          {
            "text": " is designed to derive footprint level canopy cover and vertical "
          },
          {
            "type": "a",
            "url": "https://en.wikipedia.org",
            "children": [
              {
                "text": "profile over vegetated areas"
              }
            ]
          },
          {
            "text": " between ~52°N and ~52°S.\nThe data product includes estimates of total canopy cover and PAI."
          }
        ]
      },
      {
        "type": "p",
        "children": [
          {
            "text": "The central "
          },
          {
            "text": "issues",
            "superscript": true
          },
          {
            "text": " in the definition are:"
          }
        ]
      },
      {
        "type": "ol",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether the measurement is acquired at a specific viewing angle (mostly near-nadir) or over the entire hemisphere;"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "whether a tree crown is treated as an opaque object including all small within-canopy gaps."
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Equation Example"
          }
        ],
        "id":"equation-example"
      },
      {
        "type": "equation",
        "children": [
          {
            "text": "F_{app}(x) = \\sum_{n=1}^{\\infty} \\sqrt {2^{-n} \\cdot x}"
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Image Example"
          }
        ],
        "id":"image-example"
      },
      {
        "type": "image-block",
        "children": [
          { 
            "type": "img",
            "objectKey": "fullmoon.jpg",
            "children": [ {"text": ""}]
          },
          {
            "type": "caption",
            "children": [ {"text": "This is an image caption"}]
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Table Example"
          }
        ],
        "id": "table-example" 
      },
      {
        "type": "table-block",
        "children": [
          {
            "type": "table",
            "children": [
              {
                "type": "tr",
                "children": [
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Name",
                            "bold": true
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Result",
                            "bold": true
                          }
                        ]
                      }
                    ]
                  }, 
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Date",
                            "bold": true
                          }
                        ]
                      }
                    ]
                  }
                ]
              },
              {
                "type": "tr",
                "children": [
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Lincoln"
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Inconclusive"
                          }
                        ]
                      }
                    ]
                  }, 
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "2020-01-01T00:00:00"
                          }
                        ]
                      }
                    ]
                  }
                ]
              },
              {
                "type": "tr",
                "children": [
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Bridge-water"
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "Pass"
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "td",
                    "children": [
                      {
                        "type": "p",
                        "children": [
                          {
                            "text": "2020-01-01T00:00:00"
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
            "type": "caption",
            "children": [
              {
                "text": "Test results by "
              },
              {
                "type": "a",
                "url": "http://google.com",
                "children": [
                  {
                    "text": "different"
                  }
                ]
              },
              {
                "text": " entities"
              }
            ]
          }
        ]
      },
      {
        "type": "sub-section",
        "children": [
          {
            "text": "Canopy cover types"
          }
        ], 
        "id": "canopy-cover-types"
      },
      {
        "type": "p",
        "children": [
          {
            "text": "It is different from two other widely used cover types: "
          }
        ]
      },
      {
        "type": "ul",
        "children": [
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "canopy closure defined as the proportion of the vegetation over a segment of the sky hemisphere at one point on the ground"
                  }
                ]
              }
            ]
          },
          {
            "type": "li",
            "children": [
              {
                "type": "p",
                "children": [
                  {
                    "text": "crown cover as the percentage of the ground covered by a vertical projection of the outermost perimeter of the natural spread of the foliage of plants."
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "scientific_theory_assumptions": null,
  "publication_references": [
    {
      "id": "1",
      "authors": "Dickens, Charles and Steinbeck, John",
      "title": "Example Reference",
      "series": "A",
      "edition": "3rd",
      "volume": "42ml",
      "issue": "ticket",
      "publication_place": "Boston",
      "publisher": "PenguinBooks",
      "pages": "189-198",
      "isbn": "123456789",
      "year": "1995"
    }
  ]
}'::jsonb, '{
  "creators": "Leo Thomas and Daniel da Silva and Ricardo Mestre",
  "editors": "Olaf Veerman",
  "title": "A full atbd for testing",
  "series_name": "Tests of content",
  "release_date": "2021-01-01",
  "release_place": "World Wide Web",
  "publisher": "Development Seed",
  "version": "2",
  "issue": "alpha2",
  "additional_details": "",
  "online_resource": "http://nasa-apt2-staging.s3-website-us-east-1.amazonaws.com/"
}'::jsonb, 'OPEN_REVIEW');

INSERT INTO atbd_versions_contacts (atbd_id, major, contact_id, roles)
  VALUES (1, 1, 1, ARRAY['Science contact', 'Metadata author']::e_contact_role_type[]);

INSERT INTO atbd_versions_contacts (atbd_id, major, contact_id, roles)
  VALUES (1, 1, 2, ARRAY['Investigator']::e_contact_role_type[]);

INSERT INTO atbd_versions_contacts (atbd_id, major, contact_id, roles)
  VALUES (1, 2, 2, ARRAY['Investigator']::e_contact_role_type[]);

INSERT INTO atbds (title, alias, created_by, created_at, last_updated_by, last_updated_at)
  VALUES ('Project algorithms technically overly simplistic', 'patos', :'owner_sub', '2021-03-14 14:30:00', :'owner_sub', '2021-03-15 16:00:00');

INSERT INTO atbd_versions (atbd_id, created_by, created_at, "owner", authors, last_updated_by, last_updated_at, major, minor, document, status)
  VALUES (2, :'owner_sub', '2021-03-14 14:30:00', :'owner_sub', ARRAY[:'author_sub_1', :'author_sub_2']::text[], :'owner_sub', '2021-06-27 21:00:00', 1, 0, '{
  "abstract": {
    "children": [
      {
        "type": "p",
        "children": [
          {
            "text": "The algorithm specified in this document is designed to derive footprint level canopy cover and vertical "
          }
        ]
      } 
    ] 
  },
  "version_description": null,
  "introduction": null,
  "historical_perspective": null,
  "additional_information": null,
  "data_availability":null,
  "mathematical_theory": null,
  "mathematical_theory_assumptions": null,
  "algorithm_input_variables": [],
  "algorithm_input_variables_caption": null,
  "algorithm_output_variables": [],
  "algorithm_output_variables_caption": null,
  "algorithm_usage_constraints": null,
  "performance_assessment_validation_methods": null,
  "performance_assessment_validation_uncertainties": null,
  "performance_assessment_validation_errors": null ,
  "algorithm_implementations": [],
  "data_access_input_data": [],
  "data_access_output_data": [],
  "data_access_related_urls": [],
  "journal_discussion": null,
  "journal_acknowledgements": null,
  "scientific_theory": null,
  "scientific_theory_assumptions": null,
  "publication_references": [
  ]
}'::jsonb, 'DRAFT');

INSERT INTO threads (atbd_id, major, section, created_by, last_updated_by)
  VALUES (1, 2, 'introduction', :'author_sub_1', :'author_sub_1');

INSERT INTO comments (thread_id, created_by, last_updated_by, body)
  VALUES (1, :'author_sub_1', :'author_sub_1', 'This is a first comment');

INSERT INTO comments (thread_id, created_by, last_updated_by, body)
  VALUES (1, :'author_sub_1', :'author_sub_1', 'This is a second comment')
