# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 6/1/22

from UserToolDayPattern import UserToolDayPattern, UserToolDayPatternList

class UserToolDayPatternWEngine(UserToolDayPattern):
    def grabFromDatabase(self, engine):
        connection = engine.raw_connection()
        return super().grabFromDatabase(connection)


class UserToolDayPatternListWEngine(UserToolDayPatternList):
    def grabAllFromDatabase(self, engine):
        connection = engine.raw_connection()
        return super().grabAllFromDatabase(connection)