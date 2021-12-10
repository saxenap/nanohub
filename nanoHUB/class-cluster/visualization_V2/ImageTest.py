from PIL import Image
from PIL import ImageDraw
import mysql.connector
import UserToolDayPattern

print("hello")

# conn = MySQLdb.connect(host = "localhost",
# 						user = "root",
# 						passwd = "",
# 						db = "narwhal")
conn = mysql.connector.connect(host="127.0.0.1",
                               user="shang26_ro",
                               passwd="PNY0fvkqHQfx49ry",
                               db="nanohub", port=3307)

utdpl = UserToolDayPattern.UserToolDayPatternList('2005-01-01', '2010-12-31', showCohort=False)

experimentalists = ('goguet', 'kjcho', 'kbevan', 'leog', 'fregonese', 'dkorakakis', 'xuxcn', 'ronak', 'poldiges',
                    'lbiesemans', 'pouya_hashemi', 'svoss', 'zandero', 'millercg', 'cumo12s2', 'nju2sjtu', 'mthoreson',
                    'carolinisima', 'tlow')

researchers = (
    'ssahmed', 'dkienle', 'gekco', 'lundstro', 'neophyto', 'butta', 'colbykd', 'sebgoa', 'marekk', 'seungwon', 'fsaied',
    'sciencemag', 'ebert', 'kennell', 'mmc', 'qiaowei', 'rcosby', 'clemens', 'rhee', 'ruth', 'dxu73', 'kreupl', 'cm',
    'jefonseca', 'savas', 'datta', 'mapau', 'molecule', 'laszewsk', 'pbeckett', 'rahmana', 'banerjee', 'xiats',
    'adabala', 'figueire', 'fortes', 'ammatsun', 'tsugawa', 'ming', 'liping', 'accancio', 'atomichaelbomb', 'dandrews',
    'cscohenr', 'ratner', 'bsriram', 'leland', 'djconnel', 'yergeau', 'foster', 'antoniadis', 'khaki', 'avik',
    'lsiddiqu', 'garose', 'mircea', 'mmz4s2', 'anna', 'epop', 'tboykin', 'nkharche', 'mluisier', 'melloch', 'jingw',
    'hraza', 'nicobarin', 'cfiegna', 'esangiorgi', 'ostling', 'mvh', 'kohlja', 'stevemillerband', 'vazhkudaiss',
    'albert_chin', 'tonylow', 'enzo', 'xuejieshi', 'kcantley', 'himadri', 'jihadm', 'schwarz', 'sanjay', 'abebeh',
    'shigeyasu', 'keunwookim', 'sm', 'kaushik', 'nkuri0303', 'janes', 'iaberg', 'ideretzis', 'antolam', 'profmorris',
    'anant', 'sayed', 'koswatta', 'denikonov', 'araycho', 'jk', 'ceric', 'markus_karner', 'pschwaha', 'ramesh121',
    'olearypatrick', 'shurm', 'pregaldiny', 'hamidrezah', 'amrahmadain', 'bajamar30', 'jordisune', 'gulzar', 'ravaioli',
    'guoj', 'hanantha', 'xjren', 'iwata', 'jbokor', 'shiying', 'vasileska', 'vineetchadha', 'epolizzi', 'desmiller',
    'dejia', 'hspwong', 'clarksm', 'mtmannin', 'baeh', 'bhaley', 'sunnyleekr', 'naumov', 'mprada', 'rrahman',
    'elec1020', 'rgranz', 'polyakov', 'fschwierz', 'icejenn', 'fossum', 'fgamiz', 'ge', 'tejask', 'mbraccioli',
    'hanafi', 'mrag', 'lihuiw', 'lazaro', 'oana', 'kearneyd', 'amhodge', 'curt', 'vogel', 'hongsh1221', 'ysyu71',
    'chiang', 'mmchy', 'goodnick', 'nanyun', 'onayfeh', 'seminente', 'ghibaudo', 'wakamin', 'khan530', 'paul_nano_tran',
    'carie417', 'yangliu', 'larrybiehl', 'rkalyana', 'tzpark', 'cxsong', 'lanzhao', 'futrelle', 'yliu88', 'ashraf',
    'quickboy78', 'mcgee', 'alainroy', 'quentin_rafhay', 'lloydch', 'asha0311', 'ycao17', 'saurabhr8here', 'shuiqing',
    'raman', 'jmelcher', 'andrei1970', 'musman', 'gibouria', 'gargini', 'ninad', '11degrees', 'omen', 'anhaque',
    'shikhor_himadri', 'rgolizad', 'birner', 'amressawi', 'chadwick60510', 'sumeet_kaur', 'hasan', 'sriraman',
    'yangliu1', 'svadivel', 'ppk', 'joan1026gs', 'yt', 'ragu', 'stcauley', 'jjain', 'chengkok', 'dipanjan', 'gilbertmj',
    'wilkinsn', 'abiswas5', 'bwu', 'aayanik', 'biswajit025', 'myersrr', 'huang27', 'topquark', 'saket512', 'ridha',
    'dhkim', 'groach', 'rumseyy', 'ajavey', 'destop', 'joelhoffa', 'marcuschristie', 'simonguan', 'petros', 'arrhenius',
    'wael_bibo', 'jpwolinski', 'gryn', 'jfrey', 'dkearney', 'sbanerjee', 'chonacky', 'agrawaa1', 'aganguly', 'davidiw',
    '1305test', 'damotg', 'abhijeet', 'usman', 'stanislav_markov', 'azerty', 'chaisant', 'nbutt', 'hasanm', 'xuzhiping',
    'openop', 'javiii87', 'arahman', 'deep_dd2004', 'sudeb', 'sganguly', 'rezshahab', 'sayutz', 'darve', 'ls100871',
    'liangg', 'nanotube80', 'jmurthy', 'skumar333', 'dmitrii4nanohub', 'dzemlian', 'eastach', 'pdcarpen', 'qhang',
    'gfiori', 'ianna', 'martina', 'chierold', 'dqandrews', 'mar889', 'dajoiner', 'iampgray', 'tmurphy', 'shumway',
    'mjgilbert', 'harris', 'cinedemian', 'strachan', 'apalaria', 'raseong', 'leonid', 'phaedrus', 'pawel', 'gabriel',
    'lynewman', 'gba', 'sbrophy', 'professor', 'flowers', 'nizami', 'jiangpurdue', 'yuitan87', 'saumitra', 'srogge',
    'zainu', 'sdatta', 'jvclark', 'gba2', 'lundstro2', 'mfranklin91', 'fiori', 'pvonallmen', 'rahmananisur', 'ake',
    'mourad', 'kaushik_84', 'samarthagarwal', 'wizjeong', 'kmontgo4', 'park43', 'dbeaudoin627', 'swoop', 'rmuller',
    'mcshin', 'acc', 'kkuriyan', 'jrweaver', 'reifenberger', 'pfixen', 'clarksnano', 'slee5', 'kildisha', 'narimanov',
    'uchettia', 'shalaev', 'zubinjacob', 'liuyan', 'larrybell', 'augustcharles', 'gaoyunfei', 'nikonov', 'golubok',
    'kalam', 'rdutton', 'khalidashraf', 'peizhen', 'guibber2', 'akkureshi', 'dk12', 'jpolarisj', 'msmiller',
    'kurniawano', 'djeffal', 'nacer_tech', 'cmd3', 'kholland', 'navid_p', 'janam', 'yalanz', 'iyums', 'sphinx84',
    'rahul', 'rasmita7', 'lkjoshi', 'zahidf', 'mpn', 'vrinside', 'ncnweb_kevintest4', 'maxoslemmos', 'xiao2', 'ysivan',
    'hxian', 'dutta1917', 'moonsush', 'gaoy', 'anirban', 'srmathur', 'alessandrobetti', 'kthorn01', 'redwing',
    'sumandatta', 'euler30', 'pherbcn', 'subhash', 'dnberatan', 'hadi', 'ramayya', 'irenak')
for e in researchers:
    utdp = UserToolDayPattern.UserToolDayPattern(e)
    utdp.grabFromDatabase(conn)
    utdpl.add(utdp)

utdpl.putAllToSameStartDate()

im = utdpl.makeImage()

im.show()

im.save('pureResearchers.png', 'PNG')

conn.close()