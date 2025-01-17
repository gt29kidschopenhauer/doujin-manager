from discord import DiscordException

class InvalidNuclearCode(DiscordException):
	def __init__(self, code, type, **kwargs):
		super().__init__(**kwargs)
		if type == 0:
			self.msg = "ERROR: Doujin with code " + code + " doesn't exist."
		elif type == 1:
			self.msg = "ERROR: " + code + " is not a natural number."

class InvalidInput(DiscordException):
	nameWrongPosition = 0
	invalidName = 1
	invalidFlag = 2
	invalidDate = 3
	invalidLanguage = 4
	flagWrongPosition = 5
	repetitiveFlag = 6
	invalidTimePeriod = 7

	def __init__(self, code, error_data, **kwargs):
		super().__init__(**kwargs)
		self.__error_code = code
		self.__error_data = error_data
		self.__createMsg()

	def __createMsg(self):
		if self.__error_code == self.nameWrongPosition:
			self.msg = "Invalid! The first argument should be a student's name, not '" + self.__error_data + "'!"
		elif self.__error_code == self.invalidName:
			self.msg = "Invalid! '" + self.__error_data + "' does not match to any student's name."
		elif self.__error_code == self.invalidFlag:
			self.msg = "'" + self.__error_data + "' isn't a valid flag! Use '-a', '-g', '-da', '-db' or '-l'."
		elif self.__error_code == self.invalidDate:
			self.msg = "ERROR! '" + self.__error_data + "' is not a valid date! Please use the D-M-Y format!"
		elif self.__error_code == self.invalidLanguage:
			self.msg = "The language '" + self.__error_data + "' is not supported by nhentai. The site supports japanese, chinese and english."
		elif self.__error_code == self.flagWrongPosition:
			self.msg = "Invalid! The argument should be a flag, not '" + self.__error_data + "'!"
		elif self.__error_code == self.repetitiveFlag:
			self.msg = "Repetitive flags! Multiple '" + self.__error_data + "' flags used!"
		else:
			self.msg = "Invalid! " + self.__error_data[1] + ' -> ' + self.__error_data[0] + ' is not a valid time period!'