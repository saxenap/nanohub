from visual import *
import json
import sys
import math

"""
def moveBall(ball, newX, newY):
	oldPosition = ball.pos
	oldX = oldPosition[0]
	oldY = oldPosition[1]
	steps = max(math.fabs(newX - oldX), math.fabs(newY - oldY))
	steps = int(math.floor(steps))
	for i in xrange(1, k
	"""
def verticallyOrderBalls(ballList):
	"""
	ballList.sort(key = lambda x: -x.radius)
	clusterList = []
	tempBallList = []
	tempBallList.extend(ballList)
	while len(tempBallList) > 0:
		ball = tempBallList.pop(0)
		cluster = [ball]
		tempBallList2 = []
		while len(tempBallList) > 0:
			ball2 = tempBallList.pop(0)

			
	for i in xrange(0, len(ballList)):
		for j in xrange(i, len(ballList)):k
		
	"""
	lastZ = 0
	for ball in ballList:
		ball.pos = (ball.pos[0], ball.pos[1], lastZ - ball.radius)
		lastZ = ball.pos[2] - ball.radius


colors = [(141, 211, 199), ( 255, 255, 179), ( 190, 186, 218), ( 251, 128, 114), ( 128, 177, 211), ( 253, 180, 98), ( 179, 222, 105), ( 252, 205, 229), ( 217, 217, 217), ( 188, 128, 189) ]
colors = [(228, 26, 28), ( 55, 126, 184), ( 77, 175, 74), ( 152, 78, 163), ( 255, 127, 0), ( 255, 255, 51), ( 166, 86, 40), ( 247, 129, 191)]
usableColors = []
for i in colors:
	usableColors.append((float(i[0])/255.0, float(i[1])/255.0, float(i[2])/255.0))

normalizedPopularities = json.load(open('BubbleChartData.json', 'r'))

balls = {}
scene.height = 800
scene.width = 800
scene.center = (500,500,0)
scene.range = (600, 600, 6000)
scene.fov = 0.005
theLabel = label(pos=(500, 1050, 0), text="the label")
largestBall = None

for dayUsage in normalizedPopularities:
	rate(60)
	dayInt = dayUsage[0]
	dayLabel = dayUsage[1]
	theLabel.text = dayLabel
	toolPopularities = dayUsage[2]
	scaleFactor = 1000.0
	ballList = []
	for tool in toolPopularities:
		popularities = toolPopularities[tool]
		ballX = popularities['student'] * scaleFactor
		ballY = popularities['researcher'] * scaleFactor
		ballVolume = popularities['totalUseCount']
		ballRadius = math.pow(float(ballVolume) * 3.0 / (4.0 * math.pi), (1.0/3.0))

		ball = balls.get(tool)
		if ball == None:
			ballColor = usableColors.pop(0)
			usableColors.append(ballColor)
			ball = sphere(pos=(ballX, ballY, 0), radius=ballRadius, color = ballColor)
			balls[tool] = ball
		else:
			#moveBall(ball, ballX, ballY)
			ball.pos = (ballX, ballY, 0)
			ball.radius = ballRadius
		if largestBall == None or largestBall.radius < ball.radius:
			largestBall = ball
		ballList.append(ball)

	verticallyOrderBalls(ballList)

"""
for i in xrange(0, 500):
	rate(1)
	curPosition = largestBall.pos
	curX = curPosition[0]
	curY = curPosition[1]
	curZ = curPosition[2]
	if i%2 == 0:
		largestBall.pos = (curX, curY, curZ - 500)
	else:
		largestBall.pos = (curX, curY, curZ + 500)
		
		"""
