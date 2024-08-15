# Premier-League_stats
https://cuchujr23.substack.com/p/premier-league-dataset-visualization

10 years of Premier League teams statistics for analysis

Libraries and modules to be used are imported to extract the data from a website and uploaded to AZURE. Libraries and modules were:

-Selenium: to extract the values from different links of the information found since the website has a delay time to load the information and Beautifulsoup does not work for these cases.

-Pandas: to create the dataframes and convert them into a CSV format.

-Azure: to make the connection to the container where the blobs will be stored.

-Time and Datetime: these modules were used to know the time necessary for both the execution and creation of a timestamp in a way to have a system of versions.

Step 2:

Different functions are created:

-init_driver: the driver to be used is chosen. For this case, the Chrome driver was used and an argument was added to prevent a tab from opening each time an URL is opened.

-get_element: <WebDriverWait> is used to have a delay time to open the website for loading and to find the desired value through <expected_conditions>.

-wait_for_text_change: desired element is extracted and revised before updating to make sure that it is not the same element of the first table.

-extract_team_change: URL be used by the driver is typed as well as the names and routes of the elements to be extracted. <for> is used to open each URL since more than 1 team could participate more than once for the last 10 years.

-extract_team_overview: Same as the last function but now the URL will open once per team.

-upload_to_azure: Here <connect_str> is typed to connect with both AZURE Storage and the container where CSV files will be loaded.

-main: a dictionary is created with all the teams as well as their id’s and the seasons the team played in the Premier League for the last 10 years. The driver is initiated to open the URL’S and to attach the different data to the different lists according to the information. The dataframe is created and changed to CSV format to be uploaded to AZURE storage.
