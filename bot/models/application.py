from dataclasses import dataclass


@dataclass
class Application:
    __address: str
    __cabinet: str
    __full_name: str
    __contact_number: str
    __type_of_appeal: str
    __text_message: str

    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, address: str):
        self.__address = address

    @property
    def cabinet(self) -> str:
        return self.__cabinet

    @cabinet.setter
    def cabinet(self, cabinet: str):
        self.__cabinet = cabinet

    @property
    def full_name(self) -> str:
        return self.__full_name

    @full_name.setter
    def full_name(self, full_name: str):
        self.__full_name = full_name

    @property
    def contact_number(self) -> str:
        return self.__contact_number

    @contact_number.setter
    def contact_number(self, contact_number: str):
        self.__contact_number = contact_number

    @property
    def type_of_appeal(self) -> str:
        return self.__type_of_appeal

    @type_of_appeal.setter
    def type_of_appeal(self, type_of_appeal: str):
        self.__type_of_appeal = type_of_appeal

    @property
    def text_message(self) -> str:
        return self.__text_message

    @text_message.setter
    def text_message(self, text_message: str):
        self.__text_message = text_message
