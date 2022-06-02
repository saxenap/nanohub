import sys



UNK = [' ??? ',
	   '    ?',
	   '  ?? ',
	   '  ?  ',
	   '  ?  ']
	   
A = [' AAA ',
	 'A   A',
	 'AAAAA',
	 'A   A',
	 'A   A']

B = ['BBBB ',
	 'B   B',
	 'BBBB ',
	 'B   B',
	 'BBBB ']
	 
C = [' CCCC',
	 'C    ',
	 'C    ',
	 'C    ',
	 ' CCCC']
	 
D = ['DDDD ',
	 'D   D',
	 'D   D',
	 'D   D',
	 'DDDD ']
	 
E = ['EEEEE',
	 'E    ',
	 'EEE  ',
	 'E    ',
	 'EEEEE']

F = ['FFFFF',
	 'F    ',
	 'FFF  ',
	 'F    ',
	 'F    ']

G = [' GGGG',
	 'G    ',
	 'G  GG',
	 'G   G',
	 ' GGGG']
	 
H = ['H   H',
	 'H   H',
	 'HHHHH',
	 'H   H',
	 'H   H']

I = ['IIIII',
	 '  I  ',
	 '  I  ',
	 '  I  ',
	 'IIIII']

J = ['    J',
	 '    J',
	 '    J',
	 'J   J',
	 ' JJJ ']

K = ['K   K',
	 'K  K ',
	 'KKK  ',
	 'K  K ',
	 'K   K']

L = ['L    ',
	 'L    ',
	 'L    ',
	 'L    ',
	 'LLLLL']
	 
M = ['M   M',
	 'MM MM',
	 'M M M',
	 'M   M',
	 'M   M']

N = ['N   N',
	 'NN  N',
	 'N N N',
	 'N  NN',
	 'N   N']
	 
O = [' OOO ',
	 'O   O',
	 'O   O',
	 'O   O',
	 ' OOO ']
	 
P = ['PPPP ',
	 'P   P',
	 'PPPP ',
	 'P    ',
	 'P    ']

Q = [' QQQ ',
	 'Q   Q',
	 'Q   Q',
	 'Q  QQ',
	 ' QQQQ']

R = ['RRRR ',
	 'R   R',
	 'RRRR ',
	 'R  R ',
	 'R   R']

S = [' SSSS',
	 'S    ',
	 ' SSS ',
	 '    S',
	 'SSSS ']

T = ['TTTTT',
	 '  T  ',
	 '  T  ',
	 '  T  ',
	 '  T  ']

U = ['U   U',
	 'U   U',
	 'U   U',
	 'U   U',
	 ' UUU ']

V = ['V   V',
	 'V   V',
	 'V   V',
	 ' V V ',
	 '  V  ']
	 

W = ['W   W',
	 'W   W',
	 'W W W',
	 'WW WW',
	 'W   W']

X = ['X   X',
	 ' X X ',
	 '  X  ',
	 ' X X ',
	 'X   X']

Y = ['Y   Y',
	 ' Y Y ',
	 '  Y  ',
	 '  Y  ',
	 '  Y  ']

Z = ['ZZZZZ',
	 '   Z ',
	 '  Z  ',
	 ' Z   ',
	 'ZZZZZ']

N1 = [' 1 ',
	  '11 ',
	  ' 1 ',
	  ' 1 ',
	  '111']

N2 = [' 222 ',
	  '2   2',
	  '  22 ',
	  ' 2   ',
	  '22222']

N3 = ['3333 ',
	  '    3',
	  '  33 ',
	  '    3',
	  '3333 ']

N4 = ['4   4',
	  '4   4',
	  '44444',
	  '    4',
	  '    4']

N5 = ['55555',
	  '5    ',
	  '5555 ',
	  '    5',
	  '5555 ']
	  
N6 = [' 666 ',
	  '6    ',
	  '6666 ',
	  '6   6',
	  ' 666 ']

	  
N7 = ['77777',
	  '   7 ',
	  '  7  ',
	  ' 7   ',
	  '7    ']

	  
N8 = [' 888 ',
	  '8   8',
	  ' 888 ',
	  '8   8',
	  ' 888 ']

	  
N9 = [' 999 ',
	  '9   9',
	  ' 9999',
	  '    9',
	  ' 999 ']

N0 = ['  0  ',
	  ' 0 0 ',
	  '0   0',
	  ' 0 0 ',
	  '  0  ']
	  
space = ['     ',
 	     '     ',
	     '     ',
	     '     ',
	     '     ']

percent = ['%   %',
	       '   % ',
	       '  %  ',
	       ' %   ',
	       '%   %']

comma = ['  ',
		 '  ',
		 '  ',
		 ' ,',
		 ', ']

period = [' ',
		  ' ',
		  ' ',
		  ' ',
		  '.']

apostrophe = [' \'',
			  '\' ',
			  '  ',
			  '  ',
			  '  ']

smallspace = [' ',
			  ' ',
			  ' ',
			  ' ',
			  ' ']


letterMapping = {
	'A':A,
	'B':B,
	'C':C,
	'D':D,
	'E':E,
	'F':F,
	'G':G,
	'H':H,
	'I':I,
	'J':J,
	'K':K,
	'L':L,
	'M':M,
	'N':N,
	'O':O,
	'P':P,
	'Q':Q,
	'R':R,
	'S':S,
	'T':T,
	'U':U,
	'V':V,
	'W':W,
	'X':X,
	'Y':Y,
	'Z':Z,
	'0':N0,
	'1':N1,
	'2':N2,
	'3':N3,
	'4':N4,
	'5':N5,
	'6':N6,
	'7':N7,
	'8':N8,
	'9':N9,
	' ':space,
	',':comma,
	'%':percent,
	'\'':apostrophe,
	'.':period
}


def getPlopLetterArray(s):
	rv = []
	for i in s:
		if len(rv) > 0:
			rv.append(smallspace)
		if i.upper() in letterMapping:
			rv.append(letterMapping[i.upper()])
		else:
			rv.append(UNK)
		
	return rv

def printString(s):
	a = getPlopLetterArray(s)
	if len(a) > 0:
		for i in range(0, len(a[0])):
			line = ''
			for j in a:
				line = line + j[i]
			print(line)
			
			
#printString(sys.argv[1])