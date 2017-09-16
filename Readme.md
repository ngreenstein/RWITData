# RWITData

## Installation

1. Install Python 2.7 for your platform following the [directions on python.org](https://www.python.org/downloads/).
2. If you haven’t already, download the [RWITData repository](https://github.com/ngreenstein/RWITData) from GitHub
3. Run the `RWITData.py` script in the root folder of this repository. To run a Python script, follow directions after the “Now that you've written your first program, let's run it in Python!” line of [this page](https://en.wikibooks.org/wiki/Python_Programming/Creating_Python_Programs). Replace folder paths and file names with the location of the RWITData repository on your computer and the `RWITData.py` script name. E.g. `cd ~/Desktop/RWITData; python ./RWITdata.py`
4. Open your browser to [http://localhost:8888](http://localhost:8888)

## Currently Implemented Features

Many features are still in progress, but the following work:

- Import sessions data from RWIT Online CSV files (either adding to or replacing the existing database)
- Import sessions data from SQLite files created by RWITData (either adding to or replacing the existing database)
- Export sessions data for all terms or selected terms as SQLite files

The recommended workflow for the app in its current state is:

1. Download CSV file of all sessions from RWIT Online
2. Import the CSV into RWITData (Admin -> Sessions), replacing the database
3. Export SQLite file from RWITData
4. Query/explore SQLite file from the SQLite command line tools or any database management software

When a new term’s session data is available, the recommended workflow is:

1. Download the new term’s CSV data from RWIT Online
2. Import the CSV into RWITData, adding to the database
3. Export SQLite file and continue using as described above

## Misc Info

License: BSD

To freeze, install [cx_Freeze](https://anthony-tuininga.github.io/cx_Freeze/) and run `python setup.py build`.

To run the frozen app, find the RWITData executable and run it. Keep the other files/folders in the build directory intact.