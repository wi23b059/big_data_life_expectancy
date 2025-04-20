#################################################################################
############################### LIBRARIES/IMPORTS ###############################
#################################################################################
# imports
import streamlit as st
import pandas as pd
import statsmodels.api as sm



#################################################################################
################################### MAIN-CODE ###################################
#################################################################################


#################################################################################
# Variables / data section

## session variables
if 'boolFirstrun' not in st.session_state:
    ##- bool first run
    st.session_state['boolFirstrun'] = True
    ##-- dataframe
    ##--- dataframe raw data
    ##---- tabledata
    st.session_state['dfLifeexpectancy'] = pd.DataFrame()
    st.session_state['dfAlcohol'] = pd.DataFrame()
    st.session_state['dfSmokers'] = pd.DataFrame()
    st.session_state['dfGPD'] = pd.DataFrame()
    st.session_state['dfObesity'] = pd.DataFrame()
    ##---- chartdata
    st.session_state['df_chartdata_LE'] = pd.DataFrame()
    st.session_state['df_chartdata_Alc'] = pd.DataFrame()
    st.session_state['df_chartdata_Smoker'] = pd.DataFrame()
    st.session_state['df_chartdata_GPD'] = pd.DataFrame()
    st.session_state['df_chartdata_Obesity'] = pd.DataFrame()
    ##--- dataframe merged single dependency
    st.session_state['df_merge_s_le_alc'] = pd.DataFrame()
    st.session_state['df_merge_s_le_smoker'] = pd.DataFrame()
    st.session_state['df_merge_s_le_gpd'] = pd.DataFrame()
    st.session_state['df_merge_s_le_obesity'] = pd.DataFrame()
    ##--- dataframe merged multi dependency
    st.session_state['df_merge_m_le_alc_smoker'] = pd.DataFrame()
    st.session_state['df_merge_m_le_alc_obesity'] = pd.DataFrame()
    st.session_state['df_merge_m_le_smoker_obesity'] = pd.DataFrame()
    st.session_state['df_merge_m_le_alc_smoker_obesity'] = pd.DataFrame()
    ##-- coefficient/statsmodel
    ##--- single
    st.session_state['num_coef_le_alc'] = 0
    st.session_state['num_coef_le_smoke'] = 0
    st.session_state['num_coef_le_gpd'] = 0
    st.session_state['num_coef_le_obesity'] = 0
    ##--- multi
    st.session_state['num_sm_le_alc_smoke'] = 0
    st.session_state['num_sm_le_alc_obesity'] = 0
    st.session_state['num_sm_le_smoke_obesity'] = 0
    st.session_state['num_sm_le_alc_smoke_obesity'] = 0


if(st.session_state['boolFirstrun']):
    ## local variables, only used for start
    listCountry = []
    listRelevantyears = []

    ## dataframes
    ### life_expectancy
    df_lifeexpectancy = pd.read_csv("quelldateien/life_expectancy_at_birth_years.csv")
    df_lifeexpectancy = df_lifeexpectancy.drop(["IndicatorCode","ValueType","ParentLocationCode","Location type","SpatialDimValueCode",
                                                "Period type","IsLatestYear","Dim1 type","Dim1","Dim1ValueCode","Dim2 type","Dim2",
                                                "Dim2ValueCode","Dim3 type","Dim3","Dim3ValueCode","DataSourceDimValueCode","DataSource",
                                                "FactValueNumericPrefix","FactValueUoM","FactValueNumericLowPrefix",
                                                "FactValueNumericHighPrefix","FactValueTranslationID","FactComments","Language",
                                                "DateModified"], axis=1)
    
    ### alcohol-record
    df_alcohol_records = pd.read_csv("quelldateien/alcohol_recorded_per_capita_in_litres.csv")
    df_alcohol_records = df_alcohol_records.drop(["IndicatorCode","ValueType","ParentLocationCode","Location type","SpatialDimValueCode",
                                                "Period type","IsLatestYear","Dim1 type","Dim1","Dim1ValueCode","Dim2 type","Dim2",
                                                "Dim2ValueCode","Dim3 type","Dim3","Dim3ValueCode","DataSourceDimValueCode","DataSource",
                                                "FactValueNumericPrefix","FactValueUoM","FactValueNumericLowPrefix","FactValueNumericLow",
                                                "FactValueNumericHighPrefix","FactValueNumericHigh","FactValueTranslationID",
                                                "FactComments","Language","DateModified"], axis=1)

    ### daily smokers
    years = [2005, 2010, 2015, 2020]
    filesCSV = [f"quelldateien/daily_smokers_{year}.csv" for year in years]
    df_list = []
    for year, file in zip(years, filesCSV):
        df = pd.read_csv(file, sep=";", header=2)
        df["Year"] = year
        df_list.append(df)
    df_dailysmokers_combined = pd.concat(df_list, ignore_index=True)

    ### gpd
    df_gpd = pd.read_csv("quelldateien/gpd_per_capital.csv", sep=";")
    for year in range(1980,2001):
        df_gpd = df_gpd.drop(str(year), axis=1)
    for year in range(2022,2030):
        df_gpd = df_gpd.drop(str(year), axis=1)
    df_gpd = df_gpd.fillna(0)

    ### obesity
    df_obesity = pd.read_csv("quelldateien/prevalence_of_obesity_among_adults.csv")
    df_obesity = df_obesity.drop(["IndicatorCode","ValueType","ParentLocationCode","Location type","SpatialDimValueCode",
                                "Period type","IsLatestYear","Dim1 type","Dim1","Dim1ValueCode","Dim2 type","Dim2",
                                "Dim2ValueCode","Dim3 type","Dim3","Dim3ValueCode","DataSourceDimValueCode","DataSource",
                                "FactValueNumericPrefix","FactValueUoM","FactValueNumericLowPrefix","FactValueNumericHighPrefix",
                                "FactValueTranslationID","FactComments","Language","DateModified"], axis=1)


    #################################################################################
    # data preparation

    ## methods/functions

    ### clear all dataframes from non-using countries
    def clearDFCountry(dfDirty, colName, listCountry):
        return dfDirty[dfDirty[colName].isin(listCountry)].copy()
    
    ### get all relevant years
    def getRelevantYears(dataframe):
        listRelevantyears.clear()
        for year in dataframe["Year"]:
            if(year not in listRelevantyears):
                listRelevantyears.append(year)

    ### multi-dependency modell-fitting
    def MultiDepModFit(df, colDepencevalues, colGoalvalue):
        x = df[colDepencevalues]
        y = df[colGoalvalue]
        x = sm.add_constant(x)
        modell = sm.OLS(y,x).fit()
        return modell
    
    ### create data for figures
    def createFiguredata(df, value, version):
        if df.empty: 
            return pd.DataFrame(data={'LifeExpectancy':[], 'Value':[], 'Country':[]})
        else:
            match version:
                #scatterplot
                case 1:
                    df_changed = df.pivot(index='Country', columns='Year', values=value)
                #linechart
                case 2:
                    df_changed = pd.DataFrame(data = [df.iloc[df.columns.get_loc('LifeExpectancy')],df.iloc[df.columns.get_loc(value)],df.iloc[df.columns.get_loc('Country')]])
            return df_changed

    ## get all countries from lifeexpectancy
    for country in df_lifeexpectancy["Location"]:
        if(country not in listCountry):
            listCountry.append(country)

    ## clear all dataframes again (drop every country that is not mentioned in life-expectancy)
    df_cleared_alcohol = clearDFCountry(df_alcohol_records, "Location", listCountry)
    df_cleared_smoker = clearDFCountry(df_dailysmokers_combined, "Category", listCountry)
    df_cleared_gpd = clearDFCountry(pd.melt(df_gpd, id_vars=["Country"], var_name="Year", value_name="Value"), "Country", listCountry)
    df_cleared_obesity = clearDFCountry(df_obesity, "Location", listCountry)

    ## unify some col-names
    df_reworked_lifeexpectancy = df_lifeexpectancy.rename(columns={"Location":"Country","Period":"Year", "FactValueNumeric":"LifeExpectancy"})
    df_reworked_alcohol = df_cleared_alcohol.rename(columns={"Location":"Country","Period":"Year", "FactValueNumeric":"Alcoholconsumption"})
    df_reworked_smoker = df_cleared_smoker.rename(columns={"Category":"Country"})
    df_reworked_gpd = df_cleared_gpd.copy()
    df_reworked_obesity = df_cleared_obesity.rename(columns={"Location":"Country","Period":"Year", "FactValueNumeric":"Obesityvalue"})

    ## build dataframes for analysis
    ### single dependency
    #### dependency of alcohol
    getRelevantYears(df_reworked_alcohol)
    df_filtered_LE = df_reworked_lifeexpectancy[df_reworked_lifeexpectancy["Year"].isin(listRelevantyears)]
    df_merged_LE_Alcoholrecord = pd.merge(df_reworked_alcohol, df_filtered_LE, on=["Country", "Year"], suffixes=("_LE", "_Alcohol"))
    #### dependency of smoking
    getRelevantYears(df_reworked_smoker)
    df_filtered_LE = df_reworked_lifeexpectancy[df_reworked_lifeexpectancy["Year"].isin(listRelevantyears)]
    df_filtered_Smoker = df_reworked_smoker.drop(["Men","Women"], axis=1)
    df_filtered_Smoker['Total'] = df_filtered_Smoker['Total'].str.replace(',', '.').astype(float)
    df_merged_LE_Smoker = pd.merge(df_filtered_Smoker, df_filtered_LE, on=["Country", "Year"], suffixes=("_LE", "_Smoker"))
    #### dependency of gpd
    getRelevantYears(df_reworked_gpd)
    df_filtered_LE = df_reworked_lifeexpectancy[df_reworked_lifeexpectancy["Year"].isin(listRelevantyears)]
    df_merged_LE_GPD = pd.merge(df_reworked_gpd, df_filtered_LE, on=["Country","Year"], suffixes=("_LE", "_GPD"))
    #### dependency of obesity
    getRelevantYears(df_reworked_obesity)
    df_filtered_LE = df_reworked_lifeexpectancy[df_reworked_lifeexpectancy["Year"].isin(listRelevantyears)]
    df_merged_LE_Obesity = pd.merge(df_reworked_obesity, df_filtered_LE, on=["Country", "Year"], suffixes=("_LE", "_Obesity"))
    ### multiple dependency
    #### dependency of smoker and alcohol
    getRelevantYears(df_reworked_smoker)
    df_filtered_alcohol = df_reworked_alcohol[df_reworked_alcohol["Year"].isin(listRelevantyears)]
    df_merged_LE_Alcohol_Smoker = pd.merge(df_filtered_alcohol, df_merged_LE_Smoker, on=["Country", "Year"])
    #### dependency of smoker and obesity
    df_filtered_obesity = df_reworked_obesity[df_reworked_obesity["Year"].isin(listRelevantyears)]
    df_merged_LE_Smoker_Obesity = pd.merge(df_filtered_obesity, df_merged_LE_Smoker, on=["Country", "Year"])
    ### dependency of alcohol and obesity
    df_merged_LE_Alcohol_Obesity = pd.merge(df_merged_LE_Alcoholrecord, df_filtered_obesity, on=["Country", "Year"])
    #### dependency of smoker, alcohol and obesity
    df_merged_LE_Alcohol_Smoker_Obesity = pd.merge(df_filtered_obesity, df_merged_LE_Alcohol_Smoker, on=["Country", "Year"])


    #################################################################################
    # Analyse

    ## single dependency
    correlation_s_LE_Alc = df_merged_LE_Alcoholrecord['Alcoholconsumption'].corr(df_merged_LE_Alcoholrecord['LifeExpectancy'])
    correlation_s_LE_Smoker = df_merged_LE_Smoker['Total'].corr(df_merged_LE_Smoker['LifeExpectancy'])
    corelation_s_LE_GPD = df_merged_LE_GPD['Value_GPD'].corr(df_merged_LE_GPD['LifeExpectancy'])
    correlation_s_LE_Obesity = df_merged_LE_Obesity['Obesityvalue'].corr(df_merged_LE_Obesity['LifeExpectancy'])

    ## multiple dependency
    correlation_m_LE_Alc_Smoker = MultiDepModFit(df_merged_LE_Alcohol_Smoker, ['Alcoholconsumption','Total'], 'LifeExpectancy')
    correlation_m_LE_Smoker_Obesity = MultiDepModFit(df_merged_LE_Smoker_Obesity, ['Total','Obesityvalue'], 'LifeExpectancy')
    correlation_m_LE_Alc_Obesity = MultiDepModFit(df_merged_LE_Alcohol_Obesity, ['Alcoholconsumption','Obesityvalue'], 'LifeExpectancy')
    correlation_m_LE_Alc_Smoker_Obesity = MultiDepModFit(df_merged_LE_Alcohol_Smoker_Obesity, ['Alcoholconsumption','Total', 'Obesityvalue'], 'LifeExpectancy')


    #################################################################################
    # safe data
    ##- bool first run
    st.session_state['boolFirstrun'] = False
    ##- dataframe
    ##-- dataframe raw data
    ##--- tableview
    st.session_state['dfLifeexpectancy'] = df_reworked_lifeexpectancy
    st.session_state['dfAlcohol'] = df_reworked_alcohol
    st.session_state['dfSmokers'] = df_reworked_smoker
    st.session_state['dfGPD'] = df_reworked_gpd
    st.session_state['dfObesity'] = df_reworked_obesity
    ##--- graphview
    st.session_state['df_chartdata_LE'] = createFiguredata(df_reworked_lifeexpectancy, 'LifeExpectancy', 1)
    st.session_state['df_chartdata_Alc'] = createFiguredata(df_reworked_alcohol, 'Alcoholconsumption', 1)
    st.session_state['df_chartdata_Smoker'] = createFiguredata(df_reworked_smoker, 'Total', 1)
    st.session_state['df_chartdata_GPD'] = createFiguredata(df_reworked_gpd, 'Value', 1)
    st.session_state['df_chartdata_Obesity'] = createFiguredata(df_reworked_obesity, 'Obesityvalue', 1)
    ##-- dataframe merged single dependency
    ##--- data
    st.session_state['df_merge_s_le_alc'] = df_merged_LE_Alcoholrecord
    st.session_state['df_merge_s_le_smoker'] = df_merged_LE_Smoker
    st.session_state['df_merge_s_le_gpd'] = df_merged_LE_GPD
    st.session_state['df_merge_s_le_obesity'] = df_merged_LE_Obesity
    ##--- chartdata
    st.session_state['df_merge_s_le_alc_graphdata'] = createFiguredata(df_merged_LE_Alcoholrecord, 'Alcoholconsumption', 2)
    st.session_state['df_merge_s_le_smoker_graphdata'] = createFiguredata(df_merged_LE_Smoker, 'Total', 2)
    st.session_state['df_merge_s_le_gpd_graphdata'] = createFiguredata(df_merged_LE_GPD, 'Value_GPD', 2)
    st.session_state['df_merge_s_le_obesity_graphdata'] = createFiguredata(df_merged_LE_Obesity, 'Obesityvalue', 2)
    ##-- dataframe merged multi dependency
    st.session_state['df_merge_m_le_alc_smoker'] = df_merged_LE_Alcohol_Smoker
    st.session_state['df_merge_m_le_alc_obesity'] = df_merged_LE_Alcohol_Obesity
    st.session_state['df_merge_m_le_smoker_obesity'] = df_merged_LE_Smoker_Obesity
    st.session_state['df_merge_m_le_alc_smoker_obesity'] = df_merged_LE_Alcohol_Smoker_Obesity
    ##- coefficient/statsmodel
    ##-- single
    st.session_state['num_coef_le_alc'] = correlation_s_LE_Alc
    st.session_state['num_coef_le_smoke'] = correlation_s_LE_Smoker
    st.session_state['num_coef_le_gpd'] = corelation_s_LE_GPD
    st.session_state['num_coef_le_obesity'] = correlation_s_LE_Obesity
    ##-- multi
    st.session_state['num_sm_le_alc_smoke'] = correlation_m_LE_Alc_Smoker
    st.session_state['num_sm_le_alc_obesity'] = correlation_m_LE_Smoker_Obesity
    st.session_state['num_sm_le_smoke_obesity'] = correlation_m_LE_Alc_Obesity
    st.session_state['num_sm_le_alc_smoke_obesity'] = correlation_m_LE_Alc_Smoker_Obesity



#################################################################################
#################################### WEBPAGE ####################################
#################################################################################
if not st.session_state['boolFirstrun']:


#################################################################################
    # basic structure content
    st.title("Depencies of life-expectancy")
    st.write("On this site, we will show you, which factors can affect the life-expectancy of a human")

    #################################################################################
    # Raw data
    st.header("Raw data")
    # select view 
    selectionRawdata = st.segmented_control(
        "View",
        options=["Table","Graph"],
        selection_mode='single',
        default='Table'
    )

    # table view 
    if(selectionRawdata == 'Table'):
        # select data 
        selectShowRawdata = st.selectbox(
            "Which data do you want to see?",
            ("life-expectancy","alcohol","smoker","gpd","obesity"),
            placeholder="Choose your data"
        )
        match selectShowRawdata:
                case "life-expectancy":
                    st.dataframe(st.session_state['dfLifeexpectancy'], height=360)
                case "alcohol":
                    st.dataframe(st.session_state['dfAlcohol'], height=360)
                case "smoker":
                    st.dataframe(st.session_state['dfSmokers'], height=360)
                case "gpd":
                    st.dataframe(st.session_state['dfGPD'], height=360)
                case "obesity":
                    st.dataframe(st.session_state['dfObesity'], height=360)
                case default:
                    st.write("Nothing selected")
    # graph view 
    else:
        # select data
        selectShowRawdata = st.selectbox(
            "Which data do you want to see?",
            ("life-expectancy","alcohol","smoker","gpd","obesity"),
            placeholder="Choose your data"
        )
        match selectShowRawdata:
                case "life-expectancy":
                    st.scatter_chart(st.session_state['df_chartdata_LE'], height=360)
                case "alcohol":
                    st.scatter_chart(st.session_state['df_chartdata_Alc'], height=360)
                case "smoker":
                    st.scatter_chart(st.session_state['df_chartdata_Smoker'], height=360)
                case "gpd":
                    st.scatter_chart(st.session_state['df_chartdata_GPD'], height=360)
                case "obesity":
                    st.scatter_chart(st.session_state['df_chartdata_Obesity'], height=360)
                case default:
                    st.write("Nothing selected")

    #################################################################################
    # Merged data
    st.header("Data with depency")
    # select view 
    selectionMergeddata = st.segmented_control(
        "depency",
        options=["single","multiple"],
        default='single'
    )
    ### single dependency
    if(selectionMergeddata == "single"):
        st.subheader("single dependency")
        selectShowMergeddata = st.selectbox(
            "Which data do you want to see?",
            ("alcohol","smoker","gpd","obesity"),
            placeholder="Choose your data"
        )
        match selectShowMergeddata:
            case "alcohol":
                st.line_chart(st.session_state['df_merge_s_le_alc_graphdata'], x = 'LifeExpectancy', y = 'Alcoholconsumption', color = 'Country')
                st.write("Indepedence-score: ", str(st.session_state['num_coef_le_alc']))
            case "smoker":
                st.line_chart(st.session_state['df_merge_s_le_smoker_graphdata'], x = 'LifeExpectancy', y = 'Total', color = 'Country')
                st.write("Indepedence-score: ", str(st.session_state['num_coef_le_smoke']))
            case "gpd":
                st.line_chart(st.session_state['df_merge_s_le_gpd_graphdata'], x = 'LifeExpectancy', y = 'Value', color = 'Country')
                st.write("Indepedence-score: ", str(st.session_state['num_coef_le_gpd']))
            case "obesity":
                st.line_chart(st.session_state['df_merge_s_le_obesity_graphdata'], x = 'LifeExpectancy', y = 'Obesityvalue', color = 'Country')
                st.write("Indepedence-score: ", str(st.session_state['num_coef_le_obesity']))
            case default:
                st.write("Nothing selected")
        st.write("""
             The "Independence-score" is a calculated value which can go between -1 and 1. 
             Values near -1 have a negative affect
             Values near 1 have a positive affect
             Values near 0 have not an impact
             """)
        
    ### multiple dependency
    else:
        st.subheader("multiple dependencies")
        selectShowMergeddata = st.selectbox(
            "Which data do you want to see?",
            ("alcohol & smoker","alcohol & obesity","smoker & obesity","alcohol, smoker & obesity"),
            placeholder="Choose your data"
        )
        match selectShowMergeddata:
            case "alcohol & smoker":
                st.write(st.session_state['num_sm_le_alc_smoke'].summary())
            case "alcohol & obesity":
                st.write(st.session_state['num_sm_le_alc_obesity'].summary())
            case "smoker & obesity":
                st.write(st.session_state['num_sm_le_smoke_obesity'].summary())
            case "alcohol, smoker & obesity":
                st.write(st.session_state['num_sm_le_alc_smoke_obesity'].summary())
            case default:
                st.write("Nothing selected")