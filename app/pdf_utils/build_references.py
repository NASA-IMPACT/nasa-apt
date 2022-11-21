"""
    This function helps handle references within generated PDFs
"""


def build_references(reference_dict):
    """
    Processes a reference/citation item. Returns a text string
    """
    # temp try
    try:
        print(reference_dict, "reference_dict used to generate bib reference")

        reference = ""

        for key, value in reference_dict.items():
            if not key:
                continue
            #  `series` gets changed to `journal` since `series` isn't a field used in
            # the `@article` citation type of `apacite`
            if key == "series":
                reference += f"journal={{{value}}},\n"
                continue
            if key == "authors":
                reference += f"author={{{value}}},\n"
                continue
            reference += f"{key}={{{value}}},\n"
    except Exception as e:
        raise e

    return f"@article{{\n{reference}}}"
