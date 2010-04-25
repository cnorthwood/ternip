import re
import time
import datetime
import calendar


month_days = {1: 31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31,
               9:30, 10:31, 11:30, 12:31}
seasons = ["SP", "SU", "FA", "WI"]
season_index = {"SP":0, "SU":1, "FA":2, "WI":3}

def compare_date(date1, date2, creation_year_int):
     
    pattern = re.compile(r'(\w{1,4})(?:-(\w{1,3})(?:-(\w{1,2}))?)?')
    global granularity1, granularity2, year1, year2, month1, month2, day1, day2
    
    granularity1 = date1.count('-')  #0:year 1:month 2:day
    granularity2 = date2.count('-')

    found1 = pattern.search(date1)
    found2 = pattern.search(date2)

    year1 = found1.group(1)
    year2 = found2.group(1)
     
    if(granularity1 >= 1):
        month1 = found1.group(2)
    else: month1 = 'X'
    if(granularity2 >= 1):
        month2 = found2.group(2)
    else: month2 = 'X'
     
    if(granularity1 == 2):
        day1 = found1.group(3)
    else: day1 = '0'
    if(granularity2 == 2):
        day2 = found2.group(3)
    else: day2 = '0'
        

     
    link = compare_year(year1, year2, creation_year_int)
    if(link == "VAGUE"):
        return "VAGUE"
    
    if(link == "BEFORE" or
       link == "AFTER" or
       link == "INCLUDES" or 
       link == "IS_INCLUDED" or 
       link == "IDENTITY" ):
        return link
        
    elif(link == "NEED_COMPARE_IN_YEAR"):
 
        if(granularity1 == 0 and granularity2 == 0):
            link = "IDENTITY"
            return link
        elif(granularity1 == 0):
            link = "INCLUDES"
            return link
        elif(granularity2 == 0):
            link = "IS_INCLUDED"
            return link
        else:
            link = compare_in_year()
            return link
         

def year_alpha_to_digit(year, creation_year_int):

    year_int = None
    
    if(year.isdigit()):
        year_int = int(year)
    elif(re.match("BC", year)):
        year_int = 0 - int(year[2:])
    elif(re.match("KA", year)):
        year_int = creation_year_int - int(year[2:])*1000
    elif(re.match("MA", year)):
        year_int = creation_year_int - int(year[2:])*1000000
    elif(re.match("GA", year)):
        year_int = creation_year_int - int(year[2:])*1000000000

    return year_int



        

def compare_year(year1, year2, creation_year_int):
    '''year1 and year2 both are of string type.
    return: the link between two years'''

    if(year1[0]=="X" or year2[0]=="X"):
        return "VAGUE"
    
    if(year1.isdigit() and year2.isdigit()):
        if( len(year1) == len(year2) ):
            year1_int = int(year1)
            year2_int = int(year2)
            if(need_compare_at_year_boundary(year1, year2, month1, month2, day1, day2) ):
                if( re.match(r'W', month2) ):
                    link = compare_month_week_at_year_boundary(int(year1), int(year2), int(month1), int(strip_week(month2)), int(day1), int(day2))
                    return link
                elif(re.match(r'W', month1)):
                    link = compare_month_week_at_year_boundary(int(year2), int(year1), int(month2), int(strip_week(month1)), int(day2), int(day1))
                    return reverse_link(link)
            
            if(year1_int < year2_int): #and
#               (year2_int - year1_int)!= 1 and
#               ( (month2 != "01" and month1 != "W52") or
#                 (month2 != "W1" and month1 != "12")) ):
                return "BEFORE"
            elif(year1_int > year2_int): #and
#                 (year1_int - year2_int)!=1 and
#                ( ( month1 != "01" and month2 != "W52") or
#                  ( month1 != "W1" and month2 != "12")) ):
                return "AFTER"
            else: return "NEED_COMPARE_IN_YEAR"

        else: return compare_short_year(year1, year2)

    elif(re.match("BC", year1) and re.match("BC", year2) ):
        if( len(year1[2:]) == len(year2[2:]) ):
            year1_int = year_alpha_to_digit(year1, creation_year_int)
            year2_int = year_alpha_to_digit(year2, creation_year_int)
            if(year1_int < year2_int):
                return "BEFORE"
            elif(year1_int > year2_int):
                return "AFTER"
            else: return "NEED_COMPARE_IN_YEAR"
        else:
            link_temp = compare_short_year(year1[2:], year2[2:])
            link = reverse_link(link_temp)
            return link
    else:
        year1_int = year_alpha_to_digit(year1, creation_year_int)
        year2_int = year_alpha_to_digit(year2, creation_year_int)
        if(year1_int < year2_int):
            return "BEFORE"
        elif(year1_int > year2_int):
            return "AFTER"
        else: return "NEED_COMPARE_IN_YEAR"
    
             
   # elif(year1.isdigit() or year2.isdigit()):
   #     return "ONLY_ONE_IS_PURE_DIGITAL"
    
   # else: pass




def compare_short_year(year1, year2):
    '''year1 and year2 both are of string type'''
    if( len(year1) < len(year2) ):
        year1_temp = year1
        year2_temp = year2[0:len(year1)]
        shorter_year = 1
    else: 
        year1_temp = year1[0:len(year2)]
        year2_temp = year2
        shorter_year = 2
    
    year1_int = int(year1_temp)
    year2_int = int(year2_temp)
    
    if(year1_int < year2_int): return "BEFORE"
    elif(year1_int > year2_int): return "AFTER"
    else:
        if(shorter_year == 1 ): return "INCLUDES"
        elif(shorter_year == 2): return "IS_INCLUDED"



def compare_in_year():
    
    month1_temp = month1
    month2_temp = month2
    
    month1_type = type_of_month(month1_temp)
    month2_type = type_of_month(month2_temp)
    
    #if( (granularity1 == granularity2) and 
    
    if(month1_type == "VAGUE" or month2_type == "VAGUE"):
        link = "VAGUE"
    
    if(month1_type == "SEASON" or month2_type == "SEASON"):
        link = "VAGUE"
    
    elif(month1_type == "MONTH" and month2_type == "MONTH"):
        link = compare_month(month1_temp, month2_temp)
    
    elif( (month1_type == "MONTH" and month2_type == "WEEK")
          or
          (month1_type == "WEEK" and month2_type == "MONTH")):
        link = compare_week_month(month1_temp, month2_temp)
    
#    elif( (month1_type == "MONTH" and month2_type == "SEASON")
#          or
#          (month1_type == "SEASON" and month2_type == "MONTH")):
#        link = compare_season_month(month1_temp, month2_temp)
    
    elif(month1_type == "WEEK" and month2_type == "WEEK"):
        link = compare_week(month1_temp, month2_temp) 


#    elif(month1_type == "SEASON" and month2_type == "SEASON"):
#        link = compare_season(month1_temp, month2_temp)
        
    
#    elif( (month1_type == "SEASON" and month2_type == "WEEK")
#          or
#          (month1_type == "WEEK" and month2_type == "SEASON") ):
#        link = compare_week_season(month1_temp, month2_temp)
    
    
    if(link == "BEFORE" or 
       link == "AFTER" or 
       link == "IDENTITY" or
       link == "INCLUDES" or 
       link == "IS_INCLUDED" ): 
        return link
    
    elif(link == "NEED_COMPARE_DAY"):
        if(granularity1 == 1 and granularity2 == 1):
            link = "IDENTITY"
            return link
        elif(granularity1 == 1):
            link = "INCLUDES"
            return link
        elif(granularity2 == 1):
            link = "IS_INCLUDED"
            return link
        else:
            link = compare_day(day1, day2)
            return link
        
    else: return "VAGUE"
    

def compare_week(week1, week2):
    '''week1 and week2 are strings containing 'W' indicating
    the type is week.
    Also suppose weeks do not contain 'X' '''
    return simple_compare(week1, week2)

    #finished
    

def compare_month(month1, month2):
    return simple_compare(month1, month2)

def simple_compare(time1, time2):
    '''used only in month section'''
    if(time1 < time2): return "BEFORE"
    elif(time1 > time2): return "AFTER"
    else: return "NEED_COMPARE_DAY"

#def compare_week_season(month1, month2):
#    month1_type = type_of_month(month1)
#    if(month1_type == "WEEK"):
#        #month1 is week and month2 is season
#        link = compare_week_season_aux(month1, month2)
#        return link
#    else:  #othewise month1 is season, month2 is week
#        link = compare_week_season_aux(month2, month1)
#        return reverse_link(link)

#def compare_week_season_aux(week, season):
    #according to the AHP rule, this comparison function is better
    #written after compare(season, month) and compare(month, week)
    
#    week = strip_week(week)
#    week_float = float(week)
    
#    if(season == "WI"):
#        return "VAGUE"
#    elif(season == "SP"):
#        adjust = 1.0
#    else:
#        adjust = 1.5
        
#    season_to_week_begin = (season_index[season]*3+2)*4.35 
#    season_to_week_end = season_to_week_begin + 2*4.35
    
#    if(week_float >= (season_to_week_begin + adjust)and 
#       week_float <= (season_to_week_end)): 
#        return "IS_INCLUDED"
#    elif(week_float > (season_to_week_end + adjust + 4.35)):#add 4.35 to be confident
#        return "AFTER"
#    elif(week_float < (season_to_week_begin - 4.35)): #minus 4.35 to be confident
#        return "BEFORE"
#    else: return "VAGUE"


def compare_week_month(month1, month2):
      
    month1_type = type_of_month(month1)
    
    if(month1_type == "WEEK"):
        #month1 is week, then month2 is month
        return compare_week_month_aux(month1, month2, day1, day2)
    else:
        #month2 is week and month1 is month
        link = compare_week_month_aux(month2, month1, day2, day1)
        return reverse_link(link)
 
def compare_week_month_aux(week, month, week_day, month_day): 
    #year is an integer, week is string, month is string, 
    #week_day is string, month_day is string
    week = strip_week(week)
    
    week_int = int(week)
    month_int = int(month)
    
    month_day_int = int(month_day)
    
    if(week_day == "WE"):
        week_day_int = 6
        link6 = compare_week_month_aux_aux(week_int, month_int, week_day_int, month_day_int)
        week_day_int = 7
        link7 = compare_week_month_aux_aux(week_int, month_int, week_day_int, month_day_int)
        if( (link6 == "IDENTITY" and link7 == "AFTER") or
            (link7 == "IDENTITY" and link6 == "BEFORE") ):
            return "INCLUDES"
        elif (link6 == link7):
            return link6
            
    else:
        week_day_int = int(week_day)
        
    link = compare_week_month_aux_aux(week_int, month_int, week_day_int, month_day_int)
    return link
 
def compare_week_month_aux_aux(week_int, month_int, week_day_int, month_day_int):       
    if(month_day_int == 0):
        #no month day
        month_date_begin = datetime.date(int(year1), month_int, 1)
        if(calendar.isleap(int(year1)) and month_int == 2):
           month_date_end = datetime.date(int(year1), month_int, month_days[month_int]+1)
        else: month_date_end = datetime.date(int(year1), month_int, month_days[month_int])
        
        month_to_week_begin = month_date_begin.isocalendar()
        month_to_week_end = month_date_end.isocalendar()

        #Here should be very careful as a month date when converted to week, it may fall into the week in the year before
        #or it may also fall into the week in the year after
        
        #if(int(year1) > month_to_week_begin[0] and int(year1)):
        #    return "AFTER"
        if(week_int < month_to_week_begin[1] and (int(year1) ==  month_to_week_begin[0]) ):
            return "BEFORE"
        #elif(int(year1) < month_to_week_begin[0] ):
        #    return "BEFORE"
        elif(week_int > month_to_week_end[1] and (int(year1)== month_to_week_end[0]) ):
            return "AFTER"
        elif( ( (week_int == month_to_week_begin[1]) and (int(year1)== month_to_week_begin[0]) ) or
             ( (week_int == month_to_week_end[1]) and (int(year1)== month_to_week_end[0]) ) ):
            if(week_day_int == 0):
                return "VAGUE"
            elif(week_day_int < month_to_week_begin[2]):
                return "BEFORE"
            elif(week_day_int > month_to_week_end[2]):
                return "AFTER"
        else: return "IS_INCLUDED"
            
    else:
        month_date = datetime.date(int(year1), month_int, month_day_int)
        month_to_week = month_date.isocalendar()
        if(week_int < month_to_week[1] and (int(year1) == month_to_week[0])):
            return "BEFORE"
        elif(int(year1) >  month_to_week[0]):
            return "AFTER"
        elif(week_int > month_to_week[1] and (int(year1) == month_to_week[0])):
            return "AFTER"
        elif(int(year1) < month_to_week[0]):
            return "BEFORE"
        elif( week_int == month_to_week[1]):
            if(week_day_int == 0):
                return "INCLUDES"
            elif(week_day_int > month_to_week[2]):
                return "AFTER"
            elif(week_day_int < month_to_week[2]):
                return "BEFORE"
            else: return "IDENTITY"

def compare_month_week_at_year_boundary(month_year, week_year, month, week, month_day, week_day):
    "compare month to week, parameters are all integers"
    if(month_day != 0):
        month_date = datetime.date(month_year, month, month_day)
        month_week = month_date.isocalendar()
        #put the compare year and week at place where it is called
        if(week_day != 0):
            if(month_week[2] < week_day):
                return "BEFORE"
            if(month_week[2] > week_day):
                return "AFTER"
            else: return "IDENTITY"
        else: return "IS_INCLUDED"
    else:
        if(week_day == 0):
            return "VAGUE"
        else:
            month_date = datetime.date(month_year, month, 31)
            month_week = month_date.isocalendar()
            if(month_week[2] < week_day):
                return "BEFORE"
            if(month_week[2] > week_day or month_week[2] == week_day):
                return "INCLUDES"
    
                
def need_compare_at_year_boundary(year1, year2, month1, month2, day1, day2):
    if( ( re.match(r'W', month1) and re.match(r'[^WX]', month2) ) ):
        if(int(month2) == 12):
            month_date2 = datetime.date(int(year2), int(month2), 31)
            month_week2 = month_date2.isocalendar()
        if(int(month2) == 1):
            month_date2 = datetime.date(int(year2), int(month2), 1)
            month_week2 = month_date2.isocalendar()
        else: return False
        if( int(year1) == month_week2[0] and int(strip_week(month1)) == month_week2[1]):
            return True
        else: return False
        
    elif( ( re.match(r'W', month2) and re.match(r'[^WX]', month1) ) ):
        if(int(month1) == 12):
            month_date1 = datetime.date(int(year1), int(month1), 31)
            month_week1 = month_date1.isocalendar()
        if(int(month1) == 1):
            month_date1 = datetime.date(int(year1), int(month1), 1)
            month_week1 = month_date1.isocalendar()
        else: return False
        if(int(year2) == month_week1[0] and int(strip_week(month2)) == month_week1[1]):
            return True
        else: return False
    
    else: return False
        
        
    
#def compare_week_month_aux(week, month, day):
#    
#    week = strip_week(week)
#    
#    week_float = float(week)
#    month_float = float(month)
#    
#    month_to_week_begin = (month_float-1) * 4.35  #4.35 ~ [30 or 31]/7
#    month_to_week_end = month_to_week_begin + 4.35
#    
#    if(month_float <= 6):
#        week_adjust = 1.0   #1.4 is the allowed error range
#    #as the months increases, allow larger error range 1.8
#    else: week_adjust = 1.5  
#    
#    if(day==0):
#        if(week_float >= (month_to_week_begin + week_adjust) and
#           week_float <= month_to_week_end  ):
#            return "IS_INCLUDED"
#        elif(week_float > (month_to_week_end + week_adjust) ):
#            return "AFTER"
#        elif(week_float < (month_to_week_begin)):
#            return "BEFORE"
#        else: return "VAGUE"
#    else:
#        if(week_float < (month_to_week_begin - week_adjust + day/7) ):
#            return "BEFORE"
#        elif(week_float > (month_to_week_begin + day/7) ):
#            return "AFTER"
#        else: return "VAGUE"
        
        

#def compare_season_month(month1, month2):
#
#    month1_type = type_of_month(month1)
#    if(month1_type == "MONTH"):
#        #month1 is month, month2 is season
#        return compare_season_month_aux(month1, month2)
#    else: #otherwise month1 is season, month2 is month
#        link = compare_season_month_aux(month2, month1)
#        return reverse_link(link)


#def compare_season_month_aux(month, season):
#    '''month and season are both strings'''
#    
#    month_int = int(month)
#    #not suitable for winter
#    season_to_month_begin = season_index[season]*3+3
#    season_to_month_end = season_to_month_begin + 1
#    
#    if(season == "WI"):
#        #as winter can be in the beginning of a year
#        #and also can be in the end of a year
#        #it cannot be accurately decided
#        return "VAGUE" 
#    elif(month_int >= season_to_month_begin and 
#         month_int <= season_to_month_end ): 
#        return "IS_INCLUDED"
#    elif(month_int < (season_to_month_begin - 1) ): #minus 1 to be confident
#        return "BEFORE"
#    elif(month_int > season_to_month_end + 1): #add 1 to be confident
#        return "AFTER"
#    else: return "VAGUE" #leave the two months out as vague to be confident
#
#        
#def compare_season(season1, season2):
#    '''season1 and season2 are strings indicating season'''
#    season1_temp = season1
#    season2_temp = season2
#    
#    if(season1_temp == "FA"):
#        season1_temp = "UT"     #aUTumn
#    if(season2_temp == "FA"):
#        season2_temp = "UT"    #aUTumn
#    
#    if(season1_temp == "WI" or season2_temp == "WI"):
#        return "VAGUE"
#    
#    #string comparison, a lazy way
#    if(season1_temp<season2_temp):
#        return "BEFORE"
#    elif(season1_temp>season2_temp):
#        return "AFTER"
#    else: return "IDENTITY"


def type_of_month(month):
    '''types include: "MONTH", "WEEK", "SEASON", "VAGUE" '''
    #the order of the following judgement is important as 
    #week and day can both have "X" inside
    
    if( month.find('X')>=0):
        return "VAGUE"
    if(month.isdigit()):
        return "MONTH"
    if(month[0] == "W" and month[1:].isdigit() ):
        return "WEEK"
    if(month in seasons):
        return "SEASON"



def type_of_year(year):
    if(year.find('X') >= 0 ): return "VAGUE"
    elif(year.isdigit()): return "YEAR"
    elif(year.find("BC") >= 0): return "BC"
    elif(year.find("KA") >= 0): return "KA"
    elif(year.find("MA") >= 0): return "MA"
    elif(year.find("GA") >= 0): return "GA"

def type_of_day(day):
    if(day.find('X') >= 0): return "VAGUE"
    else: return "DAY"

def compare_day(day1, day2):
    '''day1 and day2 are strings indicating day'''
    day1_type = type_of_day(day1)
    day2_type = type_of_day(day2)
    
    if(day1_type == "VAGUE" or day2_type == "VAGUE"):
        return "VAGUE"
    else:
        if(day1 < day2):
            return "BEFORE"
        elif(day1 > day2):
            return "AFTER"
        else: return "IDENTITY"

def reverse_link(link):
    if(link == "VAGUE"):
        return "VAGUE"
    elif(link == "INCLUDES"):
        return "IS_INCLUDED"
    elif(link == "IS_INCLUDED"):
        return "INCLUDES"
    elif(link == "AFTER"):
        return "BEFORE"
    elif(link == "BEFORE"):
        return "AFTER"
    elif(link == "IDENTITY"):
        return "INDENTITY"

def get_current_year():
    '''input: none
    output: integer'''
    time_obj = time.time()
    current_time = time.ctime(time_obj)
    year_string = current_time[-4:]
    year_int = int(year_string)
    return year_int

#def is_leap_year(year):
#    '''year is an integer'''
#    if( (year%400) == 0):
        
    
def strip_week(week):
    return week[1:]



