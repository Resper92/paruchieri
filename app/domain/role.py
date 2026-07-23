import enum


class Role(str, enum.Enum):
    SUPERADMIN = "superadmin"
    PARRUCCHIERE = "parrucchiere"
    CLIENT = "client"
