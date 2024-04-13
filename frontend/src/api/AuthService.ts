import axios from 'axios';
import { API_URL } from '../config';
import { CreateUserBody, LoginBody, RegisterResponse } from './models';

class AuthService {
    public async login(body: LoginBody) {
        const response = await axios.post<RegisterResponse>(`${API_URL}/user/login`, body);

        if (response.data.access_token) {
            localStorage.setItem('user', JSON.stringify(response.data));
        }

        return response.data;
    }

    public async register(body: CreateUserBody) {
        const response = await axios.post<RegisterResponse>(`${API_URL}/user`, body);

        if (response.data.access_token) {
            localStorage.setItem('user', JSON.stringify(response.data));
        }

        return response.data;
    }

    public logout(): void {
        localStorage.removeItem('user');
    }

    public getCurrentUser(): RegisterResponse | null {
        if (!localStorage.getItem('user')) {
            return null;
        }
        return JSON.parse(localStorage.getItem('user') as string);
    }

    public isAuthorized(): boolean {
        return !!this.getCurrentUser();
    }
}

export default new AuthService();
