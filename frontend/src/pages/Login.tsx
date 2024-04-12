import { Alert, Button, Checkbox, Col, Form, Input, message, Row } from 'antd';
import { useState } from 'react';
import { Link } from 'react-router-dom';

import { LockOutlined, UserOutlined } from '@ant-design/icons';

import AuthService from '../api/AuthService';
import { LoginBody } from '../api/models';

const Login = () => {
    const [messageApi, contextHolder] = message.useMessage();
    const [loading, setLoading] = useState(false);

    const onFinish = (loginForm: LoginBody) => {
        setLoading(true);
        console.log('Success:', loginForm);

        AuthService.login(loginForm)
            .then(() => {
                messageApi.success('Вы успешно авторизовались');

                setTimeout(() => {
                    window.location.href = '/home';
                }, 100);
            })
            .catch(() => {
                messageApi.error('Ошибка авторизации');
            })
            .finally(() => setLoading(false));
    };

    return (
        <>
            {contextHolder}
            <Row className='auth'>
                <Col span={6} xs={{ span: 20 }} lg={{ span: 6 }}>
                    <Alert
                        message=' Тестовый пользователь для входа. Login: vanya@edu.misis.ru, Password: test123456'
                        type='info'
                    />

                    <Form style={{ marginTop: 50 }} name='login' onFinish={onFinish}>
                        <Form.Item
                            name='email'
                            rules={[
                                {
                                    required: true,
                                    message: 'Пожалуйста, введите имя пользователя или email',
                                },
                            ]}
                        >
                            <Input
                                size='large'
                                prefix={<UserOutlined className='site-form-item-icon' />}
                                placeholder='Имя пользователя или email'
                            />
                        </Form.Item>
                        <Form.Item
                            name='password'
                            rules={[
                                {
                                    required: true,
                                    message: 'Пожалуйста, введите пароль',
                                },
                            ]}
                        >
                            <Input
                                size='large'
                                prefix={<LockOutlined className='site-form-item-icon' />}
                                type='password'
                                placeholder='Пароль'
                            />
                        </Form.Item>
                        <Form.Item>
                            <Form.Item valuePropName='checked' noStyle>
                                <Checkbox>Запомнить меня</Checkbox>
                            </Form.Item>

                            <Link to={'/signup'}>Еще нет аккаунта</Link>
                        </Form.Item>

                        <Form.Item>
                            <Button
                                block
                                type='primary'
                                htmlType='submit'
                                className='login-form-button'
                                size='large'
                                loading={loading}
                            >
                                Войти
                            </Button>
                        </Form.Item>
                    </Form>
                </Col>
            </Row>
        </>
    );
};

export default Login;
