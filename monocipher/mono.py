import sys
import random
def encryption_decryption(input_file,output_file,seed,encrypt_decrypt):
    x=list('abcdefghijklmnopqrstuvwxyz0123456789')
    x_orginal=list('abcdefghijklmnopqrstuvwxyz0123456789')
    random.Random(seed).shuffle(x)
    mapping_dictionary = dict(zip(x_orginal, x))
    ip=input_file+'.txt'
    op=output_file+'.txt'
    file1 = open(ip, "r")
    file2 = open(op, "w")
    sen=file1.read()
    sen_in=list(sen)
    if encrypt_decrypt==1:
        for i in range(len(sen_in)):
            sen_in[i]=mapping_dictionary[sen_in[i]]
    elif encrypt_decrypt==0:
        for i in range(len(sen_in)):
            for key,value in mapping_dictionary.items():
                if sen_in[i] == value:
                    sen_in[i]=key
                    break
      
    sen_out=''
    for j in sen_in:
        sen_out+=j
    file2.write(sen_out)
    file2.close()
    print(mapping_dictionary)
    
    
input_file=sys.argv[1]
output_file=sys.argv[2]
seed=int(sys.argv[3])
encrypt_decrypt=int(sys.argv[4])
if 50<=seed<=10000:
    encryption_decryption(input_file,output_file,seed,encrypt_decrypt)
else:
    print('seed needs to be in range of 50-10000')