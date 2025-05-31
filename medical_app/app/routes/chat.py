import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.chat import ChatRequest
from ..models.prediction import Prediction
from app.middleware.security import OpenAIAuth
import random

router = APIRouter()
security = OpenAIAuth()



RESPUESTAS_MEDICAS = {
    # Acné y Rosácea
    "acné": [
        "Lave suavemente el área afectada dos veces al día con un limpiador suave no comedogénico.",
        "Considere tratamientos con peróxido de benzoilo al 2.5-5% para reducir la inflamación.",
        "Evite exprimir las lesiones para prevenir cicatrices e infecciones secundarias.",
        "Para casos moderados a severos, consulte sobre opciones de retinoides tópicos o antibióticos orales.",
        "Lave suavemente el área afectada dos veces al día con un limpiador suave no comedogénico.",
        "Considere tratamientos con peróxido de benzoilo al 2.5-5% para reducir la inflamación.",
        "Evite exprimir las lesiones para prevenir cicatrices e infecciones secundarias.",
        "Para casos moderados a severos, consulte sobre opciones de retinoides tópicos o antibióticos orales.",
        "Mantenga una rutina de cuidado de la piel consistente y evite productos grasosos o comedogénicos."
    ],
    "rosácea": [
        "Identifique y evite desencadenantes comunes como alcohol, comidas picantes, estrés y temperaturas extremas.",
        "Use protección solar FPS 30+ diariamente, incluso en días nublados.",
        "Considere tratamientos tópicos con metronidazol o brimonidina para reducir el enrojecimiento.",
        "Identifique y evite desencadenantes comunes como alcohol, comidas picantes, estrés y temperaturas extremas.",
        "Use protección solar FPS 30+ diariamente, incluso en días nublados.",
        "Considere tratamientos tópicos con metronidazol o brimonidina para reducir el enrojecimiento.",
        "Para formas papulopustulares, los antibióticos orales como la doxiciclina pueden ser efectivos.",
        "Evite productos para la piel con alcohol, mentol o fragancias fuertes que puedan irritar."
    ],

    # Queratosis y Cáncer de Piel
    "queratosis actínica": [
        "Estas lesiones son precancerosas y requieren tratamiento para prevenir transformación a carcinoma.",
        "Opciones de tratamiento incluyen crioterapia, cremas de 5-fluorouracilo o terapia fotodinámica.",
        "Use protección solar rigurosa diariamente para prevenir nuevas lesiones.",
        "Estas lesiones son precancerosas y requieren tratamiento para prevenir transformación a carcinoma.",
        "Opciones de tratamiento incluyen crioterapia, cremas de 5-fluorouracilo o terapia fotodinámica.",
        "Use protección solar rigurosa diariamente para prevenir nuevas lesiones.",
        "Realice autoexámenes mensuales de piel y visite al dermatólogo anualmente para revisiones.",
        "Las lesiones persistentes o cambiantes deben ser evaluadas para descartar carcinoma escamocelular."
    ],
    "carcinoma basocelular": [
        "Este es el cáncer de piel más común pero de crecimiento lento. Requiere tratamiento quirúrgico.",
        "La escisión quirúrgica es el tratamiento estándar. Alternativas incluyen electrodesecación o cremas inmunomoduladoras.",
        "Proteja la piel del sol con ropa, sombrero y protector solar para prevenir recurrencias.",
        "Este es el cáncer de piel más común pero de crecimiento lento. Requiere tratamiento quirúrgico.",
        "La escisión quirúrgica es el tratamiento estándar. Alternativas incluyen electrodesecación o cremas inmunomoduladoras.",
        "Proteja la piel del sol con ropa, sombrero y protector solar para prevenir recurrencias.",
        "Revise regularmente su piel para detectar nuevas lesiones, especialmente en áreas expuestas al sol.",
        "Aunque raramente metastatiza, puede causar daño local significativo si no se trata."
    ],
     "carcinoma escamocelular": [
        "Requiere tratamiento oportuno debido a su potencial de metástasis.",
        "La escisión quirúrgica con márgenes adecuados es el tratamiento principal.",
        "Pacientes inmunosuprimidos tienen mayor riesgo y requieren vigilancia estrecha.",
        "Protección solar estricta es esencial para prevenir recurrencias y nuevos cánceres.",
        "Cualquier lesión que crezca rápidamente, sangre o no cure debe evaluarse urgentemente."
    ],
    "melanoma": [
        "El melanoma requiere evaluación inmediata por un especialista en cáncer de piel.",
        "El tratamiento primario es la escisión quirúrgica con márgenes adecuados.",
        "Evite la exposición solar directa y use protección FPS 50+ de amplio espectro.",
        "El melanoma requiere evaluación inmediata por un especialista en cáncer de piel.",
        "El tratamiento primario es la escisión quirúrgica con márgenes adecuados.",
        "Dependiendo de la profundidad, pueden requerirse estudios de ganglio centinela.",
        "Evite la exposición solar directa y use protección FPS 50+ de amplio espectro.",
        "Realice autoexámenes mensuales usando la regla ABCDE (Asimetría, Bordes, Color, Diámetro, Evolución)."
    ],

    # Dermatitis y Eccemas
    "dermatitis atópica": [
        "Mantenga la piel hidratada con emolientes espesos varias veces al día.",
        "Evite baños calientes prolongados; prefiera duchas cortas con agua tibia.",
        "Durante brotes, use corticosteroides tópicos de potencia adecuada según prescripción.",
        "Mantenga la piel hidratada con emolientes espesos varias veces al día.",
        "Evite baños calientes prolongados; prefiera duchas cortas con agua tibia.",
        "Durante brotes, use corticosteroides tópicos de potencia adecuada según prescripción.",
        "Identifique y evite desencadenantes como alérgenos, estrés y tejidos ásperos.",
        "Nuevos tratamientos como inhibidores de JAK pueden considerarse en casos severos."
    ],
    "dermatitis de contacto": [
        "Identifique y elimine el alérgeno o irritante causante mediante pruebas de parche.",
        "Use compresas frías para aliviar la picazón y cremas barrera para proteger la piel.",
        "Para inflamación aguda, corticosteroides tópicos de mediana potencia pueden ser útiles.",
        "Identifique y elimine el alérgeno o irritante causante mediante pruebas de parche.",
        "Use compresas frías para aliviar la picazón y cremas barrera para proteger la piel.",
        "Para inflamación aguda, corticosteroides tópicos de mediana potencia pueden ser útiles.",
        "En casos extensos, pueden requerirse corticosteroides orales por corto tiempo.",
        "Prevención es clave: use guantes protectores para sustancias irritantes."
    ],
    "dermatitis seborreica": [
        "Use champús medicados con ketoconazol, piritiona de zinc o sulfuro de selenio.",
        "En cara y cuerpo, cremas con ketoconazol o corticosteroides suaves pueden controlar brotes.",
        "Lave áreas afectadas diariamente con limpiadores suaves para reducir la acumulación de escamas.",
        "Use champús medicados con ketoconazol, piritiona de zinc o sulfuro de selenio.",
        "En cara y cuerpo, cremas con ketoconazol o corticosteroides suaves pueden controlar brotes.",
        "Lave áreas afectadas diariamente con limpiadores suaves para reducir la acumulación de escamas.",
        "El estrés puede exacerbar la condición; técnicas de manejo del estrés pueden ayudar.",
        "Para casos persistentes, considere tratamientos antiinflamatorios tópicos no esteroideos."
    ],

    # Infecciones
    "celulitis": [
        "Requiere tratamiento antibiótico inmediato, a menudo por vía intravenosa inicialmente.",
        "Mantenga la extremidad afectada elevada para reducir la hinchazón.",
        "Busque atención urgente si hay fiebre, escalofríos o rápida progresión del enrojecimiento."
    ],
    "impetigo": [
        "Mantenga las lesiones limpias y cubiertas para prevenir la diseminación.",
        "Tratamiento tópico con mupirocina para casos localizados; antibióticos orales para casos extensos.",
        "Lávese las manos frecuentemente y evite compartir toallas o artículos personales.",
        "Requiere tratamiento antibiótico inmediato, a menudo por vía intravenosa inicialmente.",
        "Mantenga la extremidad afectada elevada para reducir la hinchazón.",
        "Busque atención urgente si hay fiebre, escalofríos o rápida progresión del enrojecimiento.",
        "Controle factores predisponentes como diabetes, edema o heridas cutáneas.",
        "Complete todo el curso de antibióticos para prevenir recurrencias."
    ],
    "tinea": [
        "Use antifúngicos tópicos (clotrimazol, terbinafina) dos veces al día durante 2-4 semanas.",
        "Para infecciones extensas o en uñas, pueden requerirse antifúngicos orales.",
        "Mantenga áreas afectadas limpias y secas; use calzado ventilado para tinea pedis.",
        "Use antifúngicos tópicos (clotrimazol, terbinafina) dos veces al día durante 2-4 semanas.",
        "Para infecciones extensas o en uñas, pueden requerirse antifúngicos orales.",
        "Mantenga áreas afectadas limpias y secas; use calzado ventilado para tinea pedis.",
        "Lave toallas, ropa y sábanas con agua caliente para eliminar esporas fúngicas.",
        "Prevenga recurrencias tratando todos los miembros de la familia simultáneamente si es necesario."
    ],
    "candidiasis": [
        "Antifúngicos tópicos como nistatina o clotrimazol son efectivos para la mayoría de casos.",
        "Mantenga áreas afectadas secas; use ropa interior de algodón y evite ropa ajustada.",
        "En pacientes diabéticos, optimice el control glucémico para reducir recurrencias.",
        "Para infecciones recurrentes, considere cultivos para identificar especies resistentes.",
        "Suplementos probióticos pueden ayudar a restablecer la flora normal."
    ],

    # Enfermedades Autoinmunes
    "psoriasis": [
        "Hidratación constante con emolientes espesos ayuda a reducir escamas y picazón.",
        "Tratamientos tópicos incluyen corticosteroides, análogos de vitamina D y retinoides.",
        "Para casos moderados-severos, opciones incluyen fototerapia o biológicos.",
        "Hidratación constante con emolientes espesos ayuda a reducir escamas y picazón.",
        "Tratamientos tópicos incluyen corticosteroides, análogos de vitamina D y retinoides.",
        "Para casos moderados-severos, opciones incluyen fototerapia o biológicos.",
        "Evite desencadenantes como estrés, infecciones, trauma cutáneo y ciertos medicamentos.",
        "Revise articulaciones regularmente por signos de artritis psoriásica."
    ],
    "lupus": [
        "Protección solar estricta es fundamental; use FPS 50+ y ropa protectora.",
        "Tratamiento depende del tipo de lesiones y compromiso sistémico; puede incluir antipalúdicos.",
        "Monitoree regularmente para detección temprana de afectación renal o hematológica.",
        "Protección solar estricta es fundamental; use FPS 50+ y ropa protectora.",
        "Tratamiento depende del tipo de lesiones y compromiso sistémico; puede incluir antipalúdicos.",
        "Monitoree regularmente para detección temprana de afectación renal o hematológica.",
        "Evite medicamentos que puedan exacerbar el lupus como hidralazina y procainamida.",
        "Vacúnese según recomendaciones para pacientes inmunosuprimidos."
    ],

    # Otras condiciones
    "vitíligo": [
        "Fototerapia con UVB de banda estrecha es el tratamiento de primera línea más efectivo.",
        "Cremas tópicas con corticosteroides o inhibidores de calcineurina pueden ayudar en áreas limitadas.",
        "Protección solar rigurosa en áreas despigmentadas para prevenir quemaduras solares.",
        "Fototerapia con UVB de banda estrecha es el tratamiento de primera línea más efectivo.",
        "Cremas tópicas con corticosteroides o inhibidores de calcineurina pueden ayudar en áreas limitadas.",
        "Camuflaje cosmético y maquillaje corrector pueden mejorar la apariencia.",
        "Protección solar rigurosa en áreas despigmentadas para prevenir quemaduras solares.",
        "Nuevos tratamientos como inhibidores de JAK muestran resultados prometedores."
    ],
    "urticaria": [
        "Antihistamínicos pueden ayudar. Identifique posibles desencadenantes.",
        "Evite ropa ajustada y baños calientes. Consulte si persiste.",
        "Para casos crónicos, puede requerirse evaluación alergológica completa."
    ],
    "alopecia areata": [
        "Tratamientos incluyen corticosteroides intralesionales, tópicos o minoxidil.",
        "Para casos extensos, inmunoterapia tópica o inhibidores de JAK pueden considerarse.",
        "El apoyo psicológico es importante por el impacto emocional de la pérdida de cabello."
    ],
     # Enfermedades Ampollares e Inflamatorias
    "penfigoide ampollar": [
        "Requiere tratamiento con corticosteroides orales e inmunosupresores como azatioprina.",
        "Cuidado meticuloso de las ampollas para prevenir infecciones secundarias.",
        "Monitoreo estrecho por efectos secundarios de terapia inmunosupresora a largo plazo.",
        "La remisión puede lograrse pero recurrencias son comunes; requieren seguimiento prolongado.",
        "Vacunación contra herpes zóster antes de iniciar inmunosupresores si es posible."
    ],
    "dermatitis herpetiforme": [
        "Dieta estricta libre de gluten es fundamental para controlar la enfermedad.",
        "Dapsona es el tratamiento farmacológico principal para controlar la picazón.",
        "Monitoreo hematológico regular durante tratamiento con dapsona para prevenir anemia.",
        "Evaluación para enfermedad celíaca asociada es esencial.",
        "Suplementos nutricionales pueden ser necesarios por mala absorción asociada."
    ],
    # Infecciones Virales y Parasitarias
    "herpes": [
        "Antivirales como aciclovir, valaciclovir o famciclovir pueden acortar brotes.",
        "Terapia supresiva diaria reduce frecuencia y transmisión en herpes recurrente.",
        "Evite contacto piel con piel durante brotes activos y prodómicos.",
        "El estrés, trauma y exposición solar pueden desencadenar recurrencias.",
        "En recién nacidos o inmunosuprimidos, el herpes puede ser grave; busque atención inmediata."
    ],
    "verrugas": [
        "Tratamientos incluyen crioterapia, ácido salicílico, cantaridina o extirpación quirúrgica.",
        "Las verrugas plantares pueden requerir tratamientos más agresivos debido a dolor.",
        "Evite auto-tratamiento en área genital; requieren evaluación especializada.",
        "Las verrugas pueden desaparecer espontáneamente pero pueden tardar meses a años.",
        "Refuerce sistema inmunológico; las verrugas son más persistentes en inmunosuprimidos."
    ],
    "molusco contagioso": [
        "En inmunocompetentes, puede resolverse espontáneamente en 6-18 meses.",
        "Opciones de tratamiento incluyen curetaje, crioterapia o cremas inmunomoduladoras.",
        "Evite rascarse para prevenir autoinoculación y diseminación.",
        "En adultos con lesiones genitales, evalúe para otras infecciones de transmisión sexual.",
        "En pacientes con VIH o inmunosupresión, puede requerir tratamiento más agresivo."
    ],
    "escabiosis": [
        "Trate a todos los contactos cercanos simultáneamente para eliminar la infestación.",
        "Permetrina al 5% aplicada de cuello hacia abajo y dejada durante 8-14 horas es tratamiento de primera línea.",
        "Lave ropa de cama, toallas y prendas usadas en últimos 3 días en agua caliente (>60°C).",
        "La picazón puede persistir semanas después de tratamiento exitoso; antihistamínicos pueden ayudar.",
        "Para casos costrosos (noruega), requiere manejo especializado con ivermectina oral.",
        "Tratamientos incluyen corticosteroides intralesionales, tópicos o minoxidil.",
        "Para casos extensos, inmunoterapia tópica o inhibidores de JAK pueden considerarse.",
        "El pronóstico es variable; la mayoría recupera pelo espontáneamente en 1 año.",
        "El apoyo psicológico es importante por el impacto emocional de la pérdida de cabello.",
        "Evalúe asociación con otras enfermedades autoinmunes como tiroiditis."
    ],
    "onicomicosis": [
        "Tratamiento requiere paciencia; las uñas crecen lentamente (1-2 mm/mes).",
        "Para afectación <50% de la uña, tratamientos tópicos con amorolfina o ciclopirox.",
        "Para afectación extensa, antifúngicos orales como terbinafina o itraconazol.",
        "Desinfecte zapatos y cortaúñas para prevenir reinfección.",
        "El éxito del tratamiento se evalúa por crecimiento de uña nueva sana, no solo por resolución de síntomas."
    ],
    "melasma": [
        "Protección solar rigurosa es fundamental; use FPS 50+ y sombrero de ala ancha.",
        "Tratamientos tópicos incluyen hidroquinona, ácido azelaico, retinoides y corticosteroides.",
        "Procedimientos como peelings químicos o láser pueden complementar tratamientos tópicos.",
        "Evite desencadenantes hormonales como anticonceptivos orales si es posible.",
        "El tratamiento es prolongado; las recaídas son comunes especialmente con exposición solar."
    ],
    "hemangioma": [
        "La mayoría requieren solo observación ya que involucionan espontáneamente.",
        "Para hemangiomas problemáticos (obstrucción visual, respiratoria o ulcerados), propranolol oral es tratamiento de primera línea.",
        "La timolol tópico puede ser efectivo para hemangiomas superficiales pequeños.",
        "Ulceración es la complicación más común; requieren cuidado local meticuloso.",
        "Seguimiento regular con dermatólogo o pediatra para monitorizar crecimiento e involución."
    ],


    # Respuesta por defecto
    "default": [
        "Mantenga el área limpia y seca. Evite rascarse para prevenir infecciones secundarias.",
        "Consulte con un dermatólogo para evaluación presencial y diagnóstico preciso.",
        "Use protección solar diariamente con FPS 30+ para prevenir daño cutáneo.",
        "Observe cambios en tamaño, color, forma o síntomas de las lesiones.",
        "Evite remedios caseros no probados que puedan empeorar la condición.",
        "Mantenga el área limpia y seca. Evite rascarse para prevenir infecciones secundarias.",
        "Consulte con un dermatólogo para evaluación presencial y diagnóstico preciso.",
        "Use protección solar diariamente con FPS 30+ para prevenir daño cutáneo.",
        "Observe cambios en tamaño, color, forma o síntomas de las lesiones.",
        "Evite remedios caseros no probados que puedan empeorar la condición.",
        "Hidrate la piel regularmente con emolientes adecuados para su tipo de piel.",
        "No aplique medicamentos tópicos sin prescripción médica.",
        "Si la lesión persiste, crece o sangra, busque atención médica inmediata.",
        "Proteja las lesiones de traumatismos y exposición solar directa.",
        "Registre fotográficamente los cambios para seguimiento con su especialista."
    ]
}

MASTER_KEYWORDS = {
    "acné": ["acné", "comedones", "pápulas", "pústulas", "espinillas", "barros"],
    "rosácea": ["rosácea", "eritema", "telangiectasias", "enrojecimiento facial", "cuperosis"],
    "queratosis actínica": ["queratosis actínica", "queratosis solar", "queratosis precancerosa"],
    "carcinoma basocelular": ["carcinoma basocelular", "basocelular", "bcc", "cáncer piel no melanoma"],
    "carcinoma escamocelular": ["carcinoma escamocelular", "carcinoma epidermoide", "cáncer piel células escamosas"],
    "melanoma": ["melanoma", "nevo atípico", "cáncer piel maligno"],
    "dermatitis atópica": ["dermatitis atópica", "eccema atópico", "piel atópica"],
    "dermatitis de contacto": ["dermatitis contacto", "alérgica", "irritante", "alergia cutánea"],
    "dermatitis seborreica": ["dermatitis seborreica", "caspa", "costra láctea", "seborrea"],
    "celulitis": ["celulitis", "infección bacteriana", "erisipela"],
    "impetigo": ["impetigo", "pioderma", "infección estafilocócica"],
    "tinea": ["tinea", "dermatofitosis", "tiña", "pie de atleta", "hongo piel"],
    "candidiasis": ["candidiasis", "cándida", "infección por levaduras"],
    "psoriasis": ["psoriasis", "placas descamativas", "enfermedad piel escamosa"],
    "lupus": ["lupus", "eritematoso", "lesiones mariposa"],
    "vitíligo": ["vitíligo", "despigmentación", "manchas blancas piel"],
    "urticaria": ["urticaria", "habones", "ronchas", "alergia cutánea"],
    "alopecia areata": ["alopecia areata", "caída cabello", "calvas circulares"],
    "penfigoide ampollar": ["penfigoide ampollar", "ampollas piel", "enfermedad ampollosa"],
    "dermatitis herpetiforme": ["dermatitis herpetiforme", "ampollas pruriginosas", "enfermedad celíaca piel"],
    "herpes": ["herpes", "vesículas dolorosas", "infección por vph"],
    "verrugas": ["verrugas", "papiloma", "verruga viral"],
    "molusco contagioso": ["molusco contagioso", "pápulas perladas"],
    "escabiosis": ["escabiosis", "sarna", "ácaros piel"],
    "onicomicosis": ["onicomicosis", "hongos uñas", "uñas engrosadas"],
    "melasma": ["melasma", "manchas solares", "cloasma"],
    "hemangioma": ["hemangioma", "tumor vascular", "mancha fresa"]
}

@router.post("", response_model=dict)
async def chat_with_diagnosis(chat_req: ChatRequest, token: str = Depends(security), db: Session = Depends(get_db)):
    try:
        pred = db.query(Prediction).get(chat_req.prediction_id)
        if not pred:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")

        diagnostico = pred.diagnosis.lower()


        categoria_encontrada = None


        for categoria in RESPUESTAS_MEDICAS:
            if categoria != "default" and categoria in diagnostico:
                categoria_encontrada = categoria
                break


        if not categoria_encontrada:

            for categoria, keywords in MASTER_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in diagnostico:
                        categoria_encontrada = categoria
                        break
                if categoria_encontrada:
                    break


            if not categoria_encontrada:
                for categoria, keywords in MASTER_KEYWORDS.items():
                    if any(keyword in diagnostico for keyword in keywords):
                        categoria_encontrada = categoria
                        break


        if categoria_encontrada and categoria_encontrada in RESPUESTAS_MEDICAS:
            respuesta = random.choice(RESPUESTAS_MEDICAS[categoria_encontrada])
        else:

            respuesta = random.choice(RESPUESTAS_MEDICAS["default"])

            respuesta = f"{respuesta}"

        return {
            "diagnosis": pred.diagnosis,
            "confidence": pred.confidence,
            "recommendation": respuesta
        }

    except Exception as e:
        logging.exception("Error en el endpoint /chat")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en el servicio de chat: {str(e)}"
        )
