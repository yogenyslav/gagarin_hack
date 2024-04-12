import { User } from '.';

export interface RegisterResponse {
    token_type: string;
    access_token: string;
    user: User;
}
