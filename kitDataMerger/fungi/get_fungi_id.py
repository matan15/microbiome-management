import pandas as pd
import re


def determine_id(row):
    """
    This function determines the ID for a given row.

    Parameters:
    - row (pd.Series): A pandas Series representing a row of data.

    Returns:
    - str: The determined ID for the given row.

    If the row contains a 'group' field, the function will split the 'group' field by ',' and return the first element.
    Otherwise, it will return the 'feature_id' field.
    """
    if row["group"]:
        return row["group"].split(", ")[0]
    else:
        return row["feature_id"]


def check_incertae_sedis(row):
    """
    This function checks if the 'taxon' field of the given row contains the string "Incertae_sedis".
    If it does, it returns an empty string. Otherwise, it returns the 'group' field of the row.

    Parameters:
    - row (pd.Series): A pandas Series representing a row of data.

    Returns:
    - str: An empty string if "Incertae_sedis" is found in the 'taxon' field, otherwise the 'group' field.
    """
    if "Incertae_sedis" in row["taxon"]:
        return ""
    else:
        return row["group"]


def update_number_of_sh_incertae_sedis(row):
    """
    This function updates the 'number_of_sh' field of the given row based on whether the 'taxon' field contains the string "Incertae_sedis".

    Parameters:
    - row (pd.Series): A pandas Series representing a row of data.

    Returns:
    - int: If "Incertae_sedis" is found in the 'taxon' field, the function returns 0. Otherwise, it returns the original 'number_of_sh' value from the row.
    """
    if "Incertae_sedis" in row["taxon"]:
        return 0
    else:
        return row["number_of_sh"]


def files_to_id(asv_path, taxonomy_path, rep_path, seq, output_dir):
    feature_table = pd.read_csv(asv_path)

    try:
        feature_table = feature_table[["id", "prob"]]
    except KeyError:
        if not "id" in feature_table.columns and not "prob" in feature_table.columns:
            print("there is no columns in " + asv_path)
            return

    feature_table.reset_index(drop=True, inplace=True)

    feature_table.columns = ["taxon_name", "number_of_reads"]

    taxonomy = pd.read_csv(taxonomy_path)
    taxonomy = taxonomy[["Feature ID", "Taxon", "Consensus"]]

    taxonomy.reset_index(drop=True, inplace=True)

    taxonomy.columns = ["feature_id", "taxon", "consensus"]

    # rep_sequence=pd.read_csv(path1+"\\rep_dna-sequences.fasta", sep='>',header=None)
    # rep_sequence.dropna(inplace=True)

    rep_sequence = pd.read_csv(rep_path)

    rep_sequence = rep_sequence[["feature_id", "sequence"]]

    taxonomy.reset_index(drop=True, inplace=True)

    db_tax = pd.read_csv(
        "sh_taxonomy_qiime_ver9_99_29.11.2022.txt", sep="\t", header=None
    )
    db_tax.columns = ["group", "tax"]

    feature_table["taxon_name"] = feature_table["taxon_name"].apply(
        lambda x: re.sub(r"[^a-zA-Z]+$", "", x)
    )

    # Merge the dataframes based on Index and taxon
    merged_df1 = pd.merge(
        taxonomy, rep_sequence, left_on="feature_id", right_on="feature_id", how="inner"
    )

    merged_df2 = pd.merge(
        merged_df1, feature_table, left_on="taxon", right_on="taxon_name", how="inner"
    )

    merged_df2 = merged_df2[
        ["feature_id", "taxon", "consensus", "sequence", "number_of_reads"]
    ]
    # merged_df2=pd.merge(merged_df1, rep_sequence, left_on="feature_id", right_on="feature_id")

    # merged_df3=pd.merge(merged_df2, db_tax, left_on="taxon", right_on="tax", how="inner")

    tax_group_mapping = db_tax.set_index("tax")["group"].to_dict()

    merged_df2["group"] = merged_df2["taxon"].map(tax_group_mapping)
    merged_df2["number_of_sh"] = merged_df2["taxon"].map(
        lambda x: len(tax_group_mapping.get(x, []))
    )

    merged_df2["group"] = merged_df2["group"].fillna("")

    merged_df2["group"] = merged_df2.apply(check_incertae_sedis, axis=1)
    merged_df2["number_of_sh"] = merged_df2.apply(
        update_number_of_sh_incertae_sedis, axis=1
    )

    merged_df2["id"] = merged_df2.apply(determine_id, axis=1)

    aggregation_functions = {
        "feature_id": list,
        "consensus": "first",
        "sequence": "first",
        "number_of_reads": "first",
        "group": "first",
        "number_of_sh": "first",
        "id": "first",
    }

    merged_df3 = merged_df2.groupby("taxon").agg(aggregation_functions).reset_index()

    merged_df3.drop("sequence", axis=1, inplace=True)

    # calculate frequences
    merged_df3["number_of_reads"] = merged_df3["number_of_reads"].astype(float)
    total_reads = merged_df3["number_of_reads"].sum()

    merged_df3["freq"] = merged_df3["number_of_reads"] / total_reads

    # organize the order of the table
    order = [
        "id",
        "feature_id",
        "taxon",
        "consensus",
        "freq",
        "number_of_reads",
        "group",
        "number_of_sh",
    ]

    merged_df3 = merged_df3[order]

    # save files
    filename = asv_path.split("/")[-1]

    merged_df3.to_csv(f"{output_dir}/microbiome-public/{seq}/{filename}")
    merged_df1.to_csv(f"{output_dir}/microbiome-private/{seq}/{filename}")
