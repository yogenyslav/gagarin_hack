import axios from 'axios';
import { API_URL } from '../config';
import { Result, SendFileOrUrlResponse } from './models';

class AnomalyApiServiceInstance {
    async sendRTSPUrl(url: string): Promise<SendFileOrUrlResponse> {
        const response = await axios.post<SendFileOrUrlResponse>(`${API_URL}/stream`, {
            source: url,
        });

        return response.data;
    }

    async sendVideo(file: File): Promise<SendFileOrUrlResponse> {
        const formData = new FormData();
        formData.append('source', file);

        const response = await axios.post<SendFileOrUrlResponse>(`${API_URL}/video`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    }

    async getResult(id: number): Promise<Result> {
        const response = await axios.post<Result>(`${API_URL}/result`, { id });

        return response.data;
    }
}

export default new AnomalyApiServiceInstance();
