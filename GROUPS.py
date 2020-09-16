# -*- coding: utf-8 -*-

#make sure you pip install the necessary libraries before running the script
import pandas 
import api_calls as api
import numpy as np

def groupListGenerator():
    #get course ID 
    courseID = input("\nEnter Course ID: ").strip() 
    try:
        #api calls to gather course and student information
        courseDetails = api.getCourseDetails(courseID)
        courseName = courseDetails.get('name')
        decision = input("\nFound course \"" + courseName + "\". Hit Enter if this is the correct course or type 'change' to select a different course: ").strip()
        #if the course doesn't exist, either let the user reenter or quit the program
        while decision.lower() == "change":
            courseID = input("\nEnter Course ID: ").strip() 
            courseDetails = api.getCourseDetails(courseID)
            courseName = courseDetails.get('name')
            decision = input("\nFound course " + courseName + ". Hit Enter if this is the correct course or type 'change' to select a different course: ").strip()
        #gather the remaining single call api calls we need
        courseStudents = api.getCourseStudents(courseID)
        courseSections = api.getCourseSections(courseID)
        courseGroupCategory = api.getGroupCategory(courseID)
        #for each section in the course, get it's id and name to put into a dictionary
        courseList = {}
        for section in courseSections:
            courseList[section.get('id')] = [section.get('name')]
        #for each student create a dictionary regarding their canvas id, name, and section (used to have sis_id but doesn't work anymore)
        studentDic = {}
        for student in courseStudents:
            #since a studnet can be in multiple "sections" (lecture and tutorial, ect.) generate a list, sort list, and convert to string
            enrolledSections = []
            stringEnrolledSections = ""
            for section in student.get('enrollments'):
                enrolledSections.append(courseList[section.get('course_section_id')][0])
            enrolledSections.sort()
            for section in enrolledSections:
                stringEnrolledSections = stringEnrolledSections+section+", "
            stringEnrolledSections = stringEnrolledSections[:-2]
            studentDic[student.get('id')] = [student.get('name'), student.get('sis_user_id'), stringEnrolledSections]
        #generate variables that will be used
        spreadsheet = pandas.DataFrame(columns=['GroupSet', 'Group']) #only need these two as the amount of students varies based off of group and set
        GroupSet = ""
        Group = ""
        StudentName = ""
        StudentNumber = ""
        Section = ""
        #for each group set gather it's individual groups
        for GroupCategory in courseGroupCategory:
            courseGroupSetGroups = api.getGroups(GroupCategory.get('id'))
            GroupSet = GroupCategory.get('name')
            #for each group in a group set gather it's students and create an entry into spreadsheet
            for groupSet in courseGroupSetGroups:
                Group = groupSet.get('name')
                groupMembers = api.getGroupMembers(courseID, groupSet.get('id'))
                spreadsheet = spreadsheet.append({'GroupSet' : GroupSet, 'Group' : Group} , ignore_index=True)
                counter = 0
                #for each group member in a group in a set gather their name and section and add them in a row to a group
                for student in groupMembers:                    
                    counter = counter+1
                    if 'StudentName ' + str(counter) not in spreadsheet:
                        spreadsheet['StudentName ' + str(counter)] = ''
                        spreadsheet['StudentNumber ' + str(counter)] = ''
                        spreadsheet['Section ' + str(counter)] = ''
                    try:
                        StudentName = studentDic[student.get('user_id')][0]
                        StudentNumber = studentDic[student.get('user_id')][1]
                        Section=studentDic[student.get('user_id')][2]
                    except:
                        StudentName = 'Canvas ID: ' + student.get('user_id') + '(Not the same as SIS ID)'
                        StudentNumber = 'Canvas ID: ' + student.get('user_id') + '(Not the same as SIS ID)'
                        Section = 'Unknown'
                    spreadsheet.at[spreadsheet.index[-1], 'StudentName ' + str(counter)] = StudentName
                    spreadsheet.at[spreadsheet.index[-1], 'StudentNumber ' + str(counter)] = StudentNumber
                    spreadsheet.at[spreadsheet.index[-1], 'Section ' + str(counter)] = Section
        #Remove any nan entries and compile to a csv file
        spreadsheet = spreadsheet.replace(np.nan, '', regex=True)
        spreadsheet.to_csv(courseName+'_GroupList.csv', encoding="utf-8", index=False)
    #If the program fails in general, throw this error
    except Exception as e:
        print(e)
        decision = input("\nSomething went wrong. Perhaps you entered an invalid Canvas API Access Token or Course ID? Hit Enter to restart the program or type 'quit' to exit: ")
        if decision.lower() == "quit":
            return
        else:
            groupListGenerator()
#Starts code
if __name__ == '__main__':            
    groupListGenerator()