import pandas as pd
import numpy as np
import streamlit as st
import csv
import io

def create_config_matrix(input, fleet_species, species, biological_params, alad_setup) -> pd.DataFrame:
    # Calculated from an example sheet

    # fixed biological params
    biol_param = ["[female.lifespan]",
                  "[male.lifespan]",
                  "[sexratio]",
                  "[a.female]",
                  "[b.female]",
                  "[a.male]",
                  "[b.male]",
                  "[t0.female]",
                  "[k.female]",
                  "[linf.female]",
                  "[t0.male]",
                  "[k.male]",
                  "[linf.male]",
                  "[l50.female]",
                  "[matrange.female]",
                  "[l50.male]",
                  "[matrange.male]",
                  "[natural mortality constant]",
                  "[stock recruitment relationship]"]

    ## ROWS
    # number of empty row cells + fixed row cells
    base_rows = 20

    n_fleets = len(fleet_species)
    n_stocks = len(species)
    stocks_tot = n_stocks*5 + 6*n_stocks  # num of stocks appears 5 times; 6: empty-tool-empty-F-M-C

    total_rows = base_rows + n_fleets + stocks_tot

    ## COLUMNS
    # Columns: 1 (parameter col) + n_fleets
    if n_fleets > len(biol_param):
      total_cols = 1 + n_fleets
    else:
      total_cols = 1 + len(biol_param)

    data = np.full((total_rows, total_cols), "", dtype=object)
    df = pd.DataFrame(data)  # no headers, columns are 0..total_cols-1

    input_id = 0
    row = 0
    df.iat[row, 1] = "[case name]"
    df.iat[row, 2] = "[store path]"
    row += 1

    # Basic metadata rows
    df.iat[row, 0] = "casestudy.name"; df.iat[row, 1] = input[input_id]; input_id +=1; row += 1
    df.iat[row, 0] = "casestudy.stockno"; df.iat[row, 1] = n_stocks; row += 1
    df.iat[row, 0] = "casestudy.fleetsegmentno"; df.iat[row, 1] = n_fleets; row += 1
    df.iat[row, 0] = "casestudy.startsimulation"; df.iat[row, 1] = input[input_id]; input_id += 1; row += 1
    df.iat[row, 0] = "casestudy.endsimulation"; df.iat[row, 1] = input[input_id]; input_id += 1; row += 1

    df.iat[row, 1] = "[code]"; row += 1

    # Fleets block
    for f in range(1, n_fleets+1):
        df.iat[row, 0] = f"casestudy.F{f}"
        df.iat[row, 1] = fleet_species.iloc[f-1,0]
        row += 1

    # Blank row + [species]
    df.iat[row, 1] = "[species]"
    row += 1

    # Species
    for s in range(1, n_stocks+1):
      df.iat[row, 0] = f"casestudy.S{s}"
      df.iat[row, 1] = species.iloc[s-1,0]
      row += 1

    for f in range(1, n_fleets+1):
      df.iat[row, f] = f"[F{f}]"

    row += 1

    # Associated fleets block
    for s in range(1, n_stocks+1):
        df.iat[row, 0] = f"casestudy.S{s}.associatedFleetsegment"
        row_idx, col_idx = np.where(df == f'casestudy.S{s}')
        row_idx = row_idx[0]
        col_idx = col_idx[0] + 1

        for f in range(1, n_fleets+1):
            if df.iat[row_idx, col_idx].strip().upper() in [x.strip().upper() for x in fleet_species.iloc[f-1,1].split(",")]:  # strip().split() inserted space initially
              df.iat[row, f] = fleet_species.iloc[f-1,0]
            else:
              df.iat[row, f] = "-"
        row += 1

    # biological parameters
    for i in range(1, len(biol_param)):
      df.iat[row,i] = biol_param[i-1]

    row += 1

    # fill in biological values
    for s in range(1, n_stocks+1):
      df.iat[row, 0] = f"casestudy.S{s}.params"
      row_idx, col_idx = np.where(df == f'casestudy.S{s}')
      row_idx = row_idx[0]
      col_idx = col_idx[0] + 1
      for i in range(1, len(biol_param)):
        df.iat[row, i] = biological_params[biological_params.iloc[:,0] == df.iat[row_idx, col_idx].strip().upper()].iat[0,i]


      row += 1


    # Stock assessment tool and files for each stock
    for i in range(1, n_stocks + 1):
        df.iat[row, 1] = "[tool]"; row += 1
        df.iat[row, 0] = f"casestudy.S{i}.StockAssessmentTool"; df.iat[row, 1] = 'none'; row += 1
        df.iat[row, 1] = "[file-2007]"; row += 1
        df.iat[row, 0] = f"casestudy.S{i}.StockAss.fileF"; df.iat[row, 1] = '-'; row += 1
        df.iat[row, 0] = f"casestudy.S{i}.StockAss.fileM"; df.iat[row, 1] = '-'; row += 1
        df.iat[row, 0] = f"casestudy.S{i}.StockAss.fileC"; df.iat[row, 1] = '-'; row += 1


    df.iat[row, 1] = "[ALADYM simulation]"
    df.iat[row, 2] = "[Average years for RP and forecast]"; row += 1

    for s in range(1, n_stocks+1):
          row_idx, col_idx = np.where(df == f'casestudy.S{s}')
          row_idx = row_idx[0]
          col_idx = col_idx[0] + 1
          df.iat[row, 0] = f"casestudy.S{s}.AladymSimulation"
          df.iat[row, 1] = alad_setup[alad_setup.iloc[:,0] == df.iat[row_idx, col_idx].strip().upper()].iat[0,1]
          df.iat[row, 2] = alad_setup[alad_setup.iloc[:,0] == df.iat[row_idx, col_idx].strip().upper()].iat[0,2]
          row += 1

    eco_data = ["[Monthly VESSELS file]",
                "[Monthly DAYS.average file]",
                "[Monthly GT.average file]",
                "[Monthly KW.average file]"]

    for i in range(1, len(eco_data)+1): 
        df.iat[row, i] = eco_data[i-1]

    row += 1

    df.iat[row, 0] = "casestudy.TimeSeries.effort"; 
    for i in range(1, len(eco_data)+1):
      df.iat[row, i] = r"C:\INPUT\EFFORT\ "
    row += 1
    df.iat[row, 1] = "[Economic data file]"; row += 1
    df.iat[row, 0] = "casestudy.TimeSeries.economicData"; df.iat[row, 0] = r"C:\INPUT\ "; row += 1
    for i in range(1, n_stocks + 1):
        df.iat[row, i] = f"[S{i} production file]"
    row += 1
    
    df.iat[row, 0] = "casestudy.TimeSeries.productionData"
    for i in range(1, n_stocks+1):
        df.iat[row, i] = r"C:\INPUT\LANDINGS\ "

    row += 1

    l = ["[RP ALADYM calculation]",
        "[RP ALADYM use]",
        "[external table RPs]"]

    for i in range(1, 4):
        df.iat[row, i] = l[i-1]

    row += 1

    # Reference points per stock
    for i in range(1, n_stocks + 1):
        row_idx, col_idx = np.where(df == f'casestudy.S{s}')
        row_idx = row_idx[0]
        col_idx = col_idx[0] + 1
        df.iat[row, 0] = f"casestudy.referencepoints.S{i}"
        df.iat[row, 1] = alad_setup[alad_setup.iloc[:,0] == df.iat[row_idx, col_idx].strip().upper()].iat[0,3]
        df.iat[row, 2] = alad_setup[alad_setup.iloc[:,0] == df.iat[row_idx, col_idx].strip().upper()].iat[0,4]
        row += 1

    # Forecast years
    df.iat[row, 0] = "casestudy.startforecast"; df.iat[row, 1] = input[input_id]; input_id += 1; row += 1
    df.iat[row, 0] = "casestudy.endforecast"; df.iat[row, 1] = input[input_id]

    return df





if "show_instructions" not in st.session_state:
    st.session_state.show_instructions = True

if st.session_state.show_instructions:
    st.markdown("""
    This tool automatically creates the **configuration matrix** required for BEMTOOL.
    You will need to provide three small CSV files and a few input values.
    Currently, the paths need to be inserted once the CSV file has been downloaded.

    **Here's how it works:**
    1. **Species file** — contains one column listing all species names (e.g., `HKE`, `MUT`, `DPS`).
    2. **Fleet–Species file** — contains two columns:
      - `FleetName` — name of each fleet.
      - `TargetSpecies` — comma-separated list of species targeted by that fleet.
    3. **Biological parameters file** — one row per species with fields like `[female.lifespan]`, `[a.male]`, etc.
      - A downloadable **template** is available below to guide you.

    Below are provided CSV templates for all three files.

    The app will validate consistency between files (e.g., species names match) and generate the final configuration matrix automatically.
    """)

    st.info("""
    *Tip:* The CSV delimiter depends on your system’s locale settings.  
    Below you can download the biological parameters template with your preferred delimiter.
    When uploading the files, the app will detect the delimiter automatically.
    """)

    st.markdown("---")
    if st.button("Got it! Let's start"):
        st.session_state.show_instructions = False
        st.rerun()

else:

  st.title("File templates")

  # 1. Create a CSV template
  species_template = pd.DataFrame({
      "species": ["HKE", "MUT", "NEP"],
      })

  fleet_species_template = pd.DataFrame({
      "fleet_name": ["Fleet_A", "Fleet_B", "Fleet_C"],
      "target_species": ["HKE, MUT", "NEP", "MUT"]
      })

  biol_params_template = pd.DataFrame({
      "species": ["HKE", "MUT", "NEP"],
      "[female.lifespan]": ["","",""],
      "[male.lifespan]": ["","",""],
      "[sexratio]": ["","",""],
      "[a.female]": ["","",""],
      "[b.female]": ["","",""],
      "[a.male]": ["","",""],
      "[b.male]": ["","",""],
      "[t0.female]": ["","",""],
      "[k.female]": ["","",""],
      "[linf.female]": ["","",""],
      "[t0.male]": ["","",""],
      "[k.male]": ["","",""],
      "[linf.male]": ["","",""],
      "[l50.female]": ["","",""],
      "[matrange.female]": ["","",""],
      "[l50.male]": ["","",""],
      "[matrange.male]": ["","",""],
      "[natural mortality constant]": ["","",""],
      "[stock recruitment relationship]": ["","",""]
  })

  # 2. Convert templates to CSV for download
  species_csv = species_template.to_csv(index=False)
  fleet_species_csv = fleet_species_template.to_csv(index=False)

  st.subheader("Species template")
  st.dataframe(species_template)
  st.download_button(
      label="Download species template",
      data=species_csv,
      file_name="species_template.csv",
      mime="text/csv"
  )


  st.subheader("Fleet/species template")
  st.dataframe(fleet_species_template)
  st.download_button(
      label="Download fleet/species template",
      data=fleet_species_csv,
      file_name="fleet_species_template.csv",
      mime="text/csv"
  )


  st.subheader("Biological parameters template")
  st.dataframe(biol_params_template)
  sep_choice = st.radio(
      "Select your preferred CSV format:",
      options=[",", ";"],
      format_func=lambda x: "Comma-separated (,)" if x=="," else "Semicolon-separated (;)"
  )

  biol_params_csv = biol_params_template.to_csv(index=False, sep=sep_choice)
  st.download_button(
      label="Download biological parameters template",
      data=biol_params_csv,
      file_name="biol_params_template.csv",
      mime="text/csv"
  )




  st.title("Configuration file generation")
  st.subheader("Input values")

  # initialize the storage once
  if "user_inputs" not in st.session_state:
      st.session_state.user_inputs = []  # this will hold all inputs in order
  if "step" not in st.session_state:
      st.session_state.step = 1

  # step 1
  if st.session_state.step == 1:
      val = st.text_input("Enter case study name")
      c1, c2 = st.columns(2)

      with c1:
        if st.button("Next"):
          if val.strip():
            st.session_state.user_inputs.append(val)
            st.session_state.step += 1
            st.rerun()

  # step 2
  elif st.session_state.step == 2:
      val = st.number_input("Enter start simulation year", min_value=1900, max_value=2100)
      c1, c2 = st.columns(2)

      with c2:
        if st.button("Next"):
          st.session_state.user_inputs.append(val)
          st.session_state.step += 1
          st.rerun()

      st.divider()

      with c1:
        if st.button("Prev"):
          st.session_state.user_inputs.pop()
          st.session_state.step -= 1
          st.rerun()

  # step 3
  elif st.session_state.step == 3:
      val = st.number_input("Enter end simulation year", min_value=1900, max_value=2100)
      c1, c2 = st.columns(2)

      with c2:
        if st.button("Next"):
          st.session_state.user_inputs.append(val)
          st.session_state.step += 1
          st.rerun()

      st.divider()

      with c1:
        if st.button("Prev"):
          st.session_state.user_inputs.pop()
          st.session_state.step -= 1
          st.rerun()

  # step 4
  elif st.session_state.step == 4:
      val = st.number_input("Enter start forecast year", min_value=1900, max_value=2100)
      c1, c2 = st.columns(2)

      with c2:
        if st.button("Next"):
          st.session_state.user_inputs.append(val)
          st.session_state.step += 1
          st.rerun()

      st.divider()

      with c1:
        if st.button("Prev"):
          st.session_state.user_inputs.pop()
          st.session_state.step -= 1
          st.rerun()

  # step 5
  elif st.session_state.step == 5:
      val = st.number_input("Enter end forecast year", min_value=1900, max_value=2100)
      c1, c2 = st.columns(2)

      with c2:
        if st.button("Finish"):
          st.session_state.user_inputs.append(val)
          st.session_state.step += 1
          st.rerun()

      st.divider()

      with c1:
        if st.button("Prev"):
          st.session_state.user_inputs.pop()
          st.session_state.step -= 1
          st.rerun()

  # once all inputs are collected
  elif st.session_state.step == 6:
      st.success("All inputs collected")


  st.subheader("Upload input files")
  species_file = st.file_uploader("Upload species CSV", type=["csv"])
  fleet_species_file = st.file_uploader("Upload fleet–species CSV", type=["csv"])
  biol_params_file = st.file_uploader("Upload biological parameters CSV", type=["csv"])

  if species_file is not None:
      # Read the first 2 KB to guess the delimiter
      sample = species_file.read(2048).decode("utf-8")
      
      # Reset the pointer so pandas can read from the beginning again
      species_file.seek(0)
      
      try:
          dialect = csv.Sniffer().sniff(sample)
          delimiter_species = dialect.delimiter
      except csv.Error:
          # Default to comma if detection fails
          delimiter_species = ","

      # Read the uploaded species file into a DataFrame
      species_df = pd.read_csv(species_file, sep=delimiter_species)
      # Extract unique species from the first column, excluding the header
      sp = set(species_df.iloc[:, 0].str.strip())


  if fleet_species_file is not None:
      # Read the first 2 KB to guess the delimiter
      sample = fleet_species_file.read(2048).decode("utf-8")
      
      # Reset the pointer so pandas can read from the beginning again
      fleet_species_file.seek(0)
      
      try:
          dialect = csv.Sniffer().sniff(sample)
          delimiter_fleet = dialect.delimiter
      except csv.Error:
          # Default to comma if detection fails
          delimiter_fleet = ","

      # Read the uploaded fleet_species file into a DataFrame
      fleet_species_df = pd.read_csv(fleet_species_file, sep=delimiter_fleet)
      # Extract target species from the second column, excluding the header,
      # split the string by comma, strip whitespace, and flatten the list
      t = fleet_species_df.iloc[:, 1].apply(lambda x: [s.strip() for s in str(x).split(",")])
      tsp = set([item for sublist in t for item in sublist])

  if biol_params_file is not None:
      sample = biol_params_file.read(2048).decode("utf-8")
      biol_params_file.seek(0)
      try:
          dialect = csv.Sniffer().sniff(sample)
          delimiter_biol = dialect.delimiter
      except csv.Error:
          delimiter_biol = ","

      biol_params_df = pd.read_csv(biol_params_file, sep=delimiter_biol)
      bp = set(biol_params_df.iloc[:, 0].str.strip())







  if species_file and fleet_species_file and biol_params_file:

      missing_species_fleet = tsp - sp
      missing_species_species = sp - tsp
      missing_species_biol = bp - sp
      missing_species_biol2 = sp - bp

      if missing_species_fleet:
              st.error(f"The following species are in the fleet file but missing in species file: {missing_species_fleet}")
      elif missing_species_species:
              st.error(f"The following species are in the species file but missing in fleet file: {missing_species_species}")
      elif missing_species_biol:
              st.error(f"The following species are in the biological parameters file but missing in species file: {missing_species_biol}")
      elif missing_species_biol2:
              st.error(f"The following species are in the species file but missing in biological parameters file: {missing_species_biol2}")
      else:
              st.success("Files upload completed!")


  if species_file is not None:
    # default values
    reference_points = pd.DataFrame({
        "Species": species_df.iloc[:,0],
        "ALADYM_simulation": [True]*len(species_df.iloc[:,0]),
        "Average years for RP and forecast": [1]*len(species_df.iloc[:,0]),
        "ALADYM_reference_point_calculation": [True]*len(species_df.iloc[:,0]),
        "ALADYM_use": [True]*len(species_df.iloc[:,0])    
        })

    st.write("### ALADYM input configuration")
    edited_df = st.data_editor(reference_points)
    check = 0

    if st.button("Confirm ALADYM configuration"):
      st.session_state["reference_points_df"] = edited_df
      st.success("ALADYM config saved!")
      if "reference_points_df" in st.session_state:
        alad_input_df = st.session_state["reference_points_df"]
        check = 1

  if species_file and fleet_species_file and biol_params_file and check != 0:

      df = create_config_matrix(st.session_state.user_inputs, fleet_species_df, species_df, biol_params_df, alad_input_df)

      csv_data = df.to_csv(index=False, header=False, sep=';')
      st.download_button(
          label="Download Configuration CSV",
          data=csv_data,
          file_name="config.csv",
          mime="text/csv"
      )
