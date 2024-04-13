import axios from 'axios';
import { API_URL } from '../config';
import { Result, SendFileOrUrlResponse } from './models';

class AnomalyApiServiceInstance {
    async sendRTSPUrl(url: string): Promise<SendFileOrUrlResponse> {
        const response = await axios.post<SendFileOrUrlResponse>(
            `${API_URL}/api/detection/stream`,
            {
                source: url,
            },
            {
                headers: {
                    'ngrok-skip-browser-warning': true,
                },
            }
        );

        return response.data;
    }

    async sendVideo(file: File): Promise<SendFileOrUrlResponse> {
        const formData = new FormData();
        formData.append('source', file);

        const response = await axios.post<SendFileOrUrlResponse>(
            `${API_URL}/api/detection/video`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'ngrok-skip-browser-warning': true,
                },
            }
        );

        return response.data;
    }

    async getResult(id: number): Promise<Result> {
        const response = await axios.get<Result>(`${API_URL}/api/detection/result/${id}`, {
            headers: {
                'ngrok-skip-browser-warning': true,
            },
        });

        return response.data;
    }

    async cancel(id: number): Promise<void> {
        await axios.post(`${API_URL}/api/detection/cancel/${id}`, null, {
            headers: {
                'ngrok-skip-browser-warning': true,
            },
        });
    }
}

export default new AnomalyApiServiceInstance();
