import { RegisterResponse } from '../api/models';

export default function authHeader() {
    if (localStorage.getItem('user') == null) {
        return {};
    }
    const user: RegisterResponse = JSON.parse(localStorage.getItem('user') as string);

    if (user && user.access_token) {
        return { Authorization: 'Bearer ' + user.access_token };
    }

    return {};
}
