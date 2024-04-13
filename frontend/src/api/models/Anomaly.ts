import { AnomalyClass, AnomalyStatus, AnomalyType } from '../constants';

export interface Anomaly {
    ts: number;
    link: string[];
    class: AnomalyClass;
}
// Если type == ‘STREAM’, то ts - unix timestamp
// Если type == ‘VIDEO’, ts - количество секунд от начала

export interface Result {
    type: AnomalyType;
    status: AnomalyStatus;
    anomalies: Anomaly[];
}

export interface ResultParams {
    id: number;
}

export interface SendFileOrUrlResponse {
    id: number;
}

export interface VideoQueryParams {
    source: File;
}

export interface StreamQueryParams {
    source: string;
}

export interface SendArchiveResponse {
    ids: number[];
}
