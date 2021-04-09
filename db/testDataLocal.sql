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
    (title, alias, created_by, last_updated_by)
VALUES
    ('Test ATBD 1', 'test-atbd-1', 'LeoThomas123', 'LeoThomas123');

INSERT INTO atbd_versions
    (atbd_id, created_by, last_updated_by, major, minor, document, citation, status)
VALUES
    (1, 'LeoThomas123', 'LeoThomas123', 1, 0, '{
  "introduction": null,
  "historical_perspective": null,
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
  "performance_assessment_validation_errors": {
    "invalid": "this will be invalid"
  },
  "algorithm_implementations": [
    {
      "url": "https://developmentseed.org",
      "description": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "This is our website"
              }
            ]
          }
        ]
      }
    },
    {
      "url": "https://google.com",
      "description": {
        "invalid": "this will be invalid"
      }
    }
  ],
  "data_access_input_data": [],
  "data_access_output_data": [
    {
      "url": "https://youtube.com",
      "description": {
        "children": [
          {
            "type": "p",
            "children": [
              {
                "text": "This is basically a link to youtube"
              }
            ]
          }
        ]
      }
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
            "text": "Canopy cover types"
          }
        ]
      },
      {
        "type": "img",
        "objectKey": "fullmoon.jpg",
        "children": [
          {
            "text": "Image of the full moon - 2019"
          }
        ]
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
  "scientific_theory_assumptions": {
    "invalid": "this will be invalid"
  },
  "publication_references": [
    {
      "publication_reference_id": 1,
      "authors": "Dickens, Charles and Steinbeck, John",
      "title": "Example Reference",
      "series": "A",
      "edition": "3rd",
      "volume": "42ml",
      "issue": "ticket",
      "publication_place": "Boston",
      "publisher": "PenguinBooks",
      "pages": "189-198",
      "isbn": 123456789,
      "year": 1995
    }
  ]
}', '{
  "creators": "Leo Thomas, Daniel da Silva, Ricardo Mestre",
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
}',
        'Published');

INSERT INTO atbd_versions
    (atbd_id, created_by, last_updated_by, major, minor, document)
VALUES
    (1, 'LeoThomas123', 'LeoThomas123', 2, 0, '{
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
                        "text": "Canopy cover types"
                    }
                ]
            },
            {
                "type": "img",
                "objectKey": "fullmoon.jpg",
                "children": [
                    {
                        "text": "Image of the full moon - 2019"
                    }
                ]
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
    "introduction": null,
    "historical_perspective": null,
    "algorithm_input_variables": [],
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
    "publication_references": [
        {
            "publication_reference_id": 1,
            "authors": "Dickens, Charles and Steinbeck, John",
            "title": "Example Reference",
            "series": "A",
            "edition": "3rd",
            "volume": "42ml",
            "issue": "ticket",
            "publication_place": "Boston",
            "publisher": "PenguinBooks",
            "pages": "189-198",
            "isbn": 123456789,
            "year": 1996
        }
    ]
}');
        