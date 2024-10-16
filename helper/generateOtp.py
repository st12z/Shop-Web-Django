import random
def generateOtp(length):
  s="0123456789" 
  txt=""
  for i in range(0,length):
    txt+=s[random.randint(1,len(s)-1)];
  return txt