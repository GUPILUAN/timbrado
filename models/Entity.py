class Person:
    def __init__(
        self,
        rfc: str,
        nombre: str,
        regimen_fiscal: str,
        domicilio_fiscal: str | None = None,
        uso_cfdi: str | None = None,
    ):
        self.rfc: str = rfc
        self.nombre: str = nombre
        self.regimen_fiscal: str = regimen_fiscal
        self.domicilio_fiscal: str | None = domicilio_fiscal
        self.uso_cfdi: str | None = uso_cfdi

    def __repr__(self):
        return (
            f"Persona Moral o Física(rfc={self.rfc}, nombre={self.nombre}, regimen_fiscal={self.regimen_fiscal}, "
            f"uso_cfdi={self.uso_cfdi}, domicilio_fiscal={self.domicilio_fiscal})"
        )
