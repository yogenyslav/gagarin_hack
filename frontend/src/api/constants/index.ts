export enum AnomalyClass {
    BLUR = 'BLUR',
    LIGHT = 'LIGHT',
    MOTION = 'MOTION',
    OVERLAP = 'OVERLAP',
}

export enum AnomalyStatus {
    PROCESSING = 'PROCESSING',
    SUCCESS = 'SUCCESS',
    ERROR = 'ERROR',
    CANCELED = 'CANCELED',
}

export enum AnomalyType {
    STREAM = 'STREAM',
    VIDEO = 'VIDEO',
}

export const anomalyClassRegistry: Record<AnomalyClass, string> = {
    [AnomalyClass.BLUR]: 'Размытие',
    [AnomalyClass.LIGHT]: 'Свет',
    [AnomalyClass.MOTION]: 'Движение',
    [AnomalyClass.OVERLAP]: 'Перекрытие',
};

export const anomalyStatusRegistry: Record<AnomalyStatus, string> = {
    [AnomalyStatus.PROCESSING]: 'Обработка',
    [AnomalyStatus.SUCCESS]: 'Обработка успешно завершена',
    [AnomalyStatus.ERROR]: 'Ошибка',
    [AnomalyStatus.CANCELED]: 'Отменено',
};

export const anomalyTypeRegistry: Record<AnomalyType, string> = {
    [AnomalyType.STREAM]: 'Трансляция',
    [AnomalyType.VIDEO]: 'Видео',
};
