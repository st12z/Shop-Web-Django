import random
def generateString(length):
  s="abcdefghijklmnopqrstuvwxyz0123456789" 
  txt=""
  for i in range(0,length):
    txt+=s[random.randint(1,len(s)-1)];
  return txt