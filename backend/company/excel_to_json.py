import pandas as pd
import openpyxl
def csvtolist(pathoffile):
# df=pd.read_csv("C:/Development/Web-Dev/Project-1/Semester_project/backend/mlmodel/data.csv")
    df=pd.read_csv(pathoffile)
# print(df)
    questions=df["question"]
    answers=df["answer"]
    difficulties=df["difficulties"]
    questionSet=[]
    for i in range(len(df)):
        dit={
            "question": questions[i],
            "answer": answers[i],
            "difficulty": difficulties[i]
        }
        questionSet.append(dit)
    return questionSet


def exceltolist(file_path):
    import pandas as pd

    # Load the Excel file
    excel_data = pd.ExcelFile(file_path)

    # Parse the relevant sheet (assuming it's named 'Viva')
    viva_data = excel_data.parse('Viva')

    # Extract structured data starting from the appropriate row (adjusted based on earlier observation)
    # Columns of interest: NOS (Unnamed: 1), PCS (MEP/Q7102), Question (Unnamed: 4), Model_Answer (Unnamed: 5)
    structured_data = viva_data.iloc[6:, [1, 2, 3, 4, 5]]
    structured_data.columns = ['NOS', 'PCS', 'Difficulty', 'Question', 'Answer']

    # Drop rows where all values are NaN
    structured_data = structured_data.dropna(how='all')

    # Fill missing NOS values with forward fill, assuming NOS is shared until a new one appears
    # structured_data['NOS'] = structured_data['NOS'].fillna(method='ffill')
    structured_data = structured_data.dropna(subset=['Question', 'Answer'])

    # Convert the DataFrame to a list of dictionaries
    questionSet = []
    NOS=[]
    count=0
    for _, row in structured_data.iterrows():
        if pd.isna(row['NOS']):
            print("empty nos at line row:",count+1)
            return [] ,0
        question_entry = {
            "NOS": row['NOS'],
            "PCS": 'undefined' if pd.isna(row['PCS']) else row['PCS'],
            "difficulty": 'undefined' if pd.isna(row['Difficulty']) else row['Difficulty'],
            "question": row['Question'],
            "answer": row['Answer']
        }
        count=count+1
        if row['NOS'] not in NOS:
            NOS.append(row['NOS'])
        questionSet.append(question_entry)

    return questionSet , len(NOS)




# # Example usage
# file_path = "MEPQ7101 Armed Security Guard.xlsx"  # Replace with your actual file path
# extract_data_to_json(file_path)
