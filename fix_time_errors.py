from datetime import datetime
from itertools import count
from tqdm import tqdm
import os
TIMESTAMP_FORMAT = "%H:%M:%S,%f"
alternate_time_step_formats=[]
TIMESTAMP_SEPARATOR = " --> "
os.makedirs("time_fixed",exist_ok=True)
errors=0
def parse_timestamps(line: str):
    try:
        start, end = line.split(TIMESTAMP_SEPARATOR)

        start = datetime.strptime(start, TIMESTAMP_FORMAT).time()
        end = datetime.strptime(end, TIMESTAMP_FORMAT).time()
    except:
        
        start = datetime.strptime(start, TIMESTAMP_FORMAT).time()
        end = datetime.strptime(end, TIMESTAMP_FORMAT).time()
    return start,end

def extract_hms(part,segment:int=1):
    part1=""
    nums1=""
    for _ in part:
        if _>='0' and _<='9':
            nums1+=_
    
    if len(nums1)>=6:
        part1=f"{nums1[0:2]}:{nums1[2:4]}:{nums1[4:6]}"
        
    if len(nums1)>=9:       
        part3="".join(nums1[6:])
    elif len(nums1)>=6 and len(nums1)<9 and segment==1:
        part3="020"
    elif len(nums1)>=6  and len(nums1)<9 and segment==2:
        part3="040"
    
    if not part1 and segment==1:
        part1="00:00:00"
        part3="020"
    if not part1 and segment==2:
        part1="00:00:00"
        part3="040"
        
    return part1+","+part3


def add_padding(s:str):
    if len(s)==1:
        s="0"+s
    return s

def fix_hms_limit(part):
    try:
        h,m,s=part.split(",")[0].split(":")
        mil=part.split(",")[1]
        
        h=str(int(h)%24)
        h=add_padding(h)
        m=str(int(m)%60)
        m=add_padding(m)
        s=str(int(s)%60)
        s=add_padding(s)
    
            
        mil=str(int(str(mil).strip())%1000000)
        return f"{h}:{m}:{s},{mil}"
    except Exception as e:
        print(f"Can not fix in {part}. {e}")
        
def convert_to_correct_format(line)->str:
    """
    Fixes the formatting  issues as seen on file_with_time_errors.txt
    
    
    """
    global errors
    part1,part2=line.split(TIMESTAMP_SEPARATOR)
    new_part_1=extract_hms(part1,1)
    new_part_2=extract_hms(part2,2)
    
    new_part_1=fix_hms_limit(new_part_1)
    new_part_2=fix_hms_limit(new_part_2)
    
    
    try:
        start = datetime.strptime(new_part_1, TIMESTAMP_FORMAT).time()
        end = datetime.strptime(new_part_2, TIMESTAMP_FORMAT).time()
    except Exception as e:
        print(f"Error: {e} in {new_part_1} --> {new_part_2}")
        print("-------")
        errors+=1
    
    return new_part_1+TIMESTAMP_SEPARATOR+new_part_2
            
        

            
def parse_lines(path):
    index = count(0)
    data=[]
        
    with open(path, mode="r+",encoding="UTF-8",errors="replace") as file:
       
        for line in file:
            line = line.strip()
            data.append(line)
    
    for _ in range(0,len(data)):
        line=data[_]

        if TIMESTAMP_SEPARATOR in line:
            line=convert_to_correct_format(line)
            
        data[_]=line
    
    file_save_path="time_fixed//"+path.split("//")[-1]
    
    with open(file_save_path, "w+", encoding="UTF-8",errors="replace") as file:
        for line in data:
            file.write(line+"\n")

if __name__=='__main__':
    data=None
    with open(f"files_with_time_error.txt",mode="r",encoding="UTF-8") as file:
        data=file.read()
    
    extract_defected_file_paths=["//".join(list(line.split(":")[-1].strip()[:-5:-1])) for line in data.split("\n")]
    extract_defected_file_names=["//"+line.split(":")[-1].strip()+".srt" for line in data.split("\n")]
    counter=0
    
    
    for c,file_path in tqdm(enumerate(extract_defected_file_paths),total=len(extract_defected_file_names)):
        fpath="files//"+file_path+extract_defected_file_names[c]
        if os.path.isfile(fpath):
           parse_lines(fpath)
           counter+=1
    print(f"Total fixed: {counter}")
    print(f"Number of errors: {errors}")
    
    

    #single file
    #path="files//0//0//8//6//1957976800.srt"
    #parse_lines(path)
    
    