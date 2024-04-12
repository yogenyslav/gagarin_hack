import { Button, Checkbox, Col, Form, Input, message, Row } from 'antd';
import { useState } from 'react';
import { Link } from 'react-router-dom';

import { LockOutlined, MailOutlined, UserOutlined } from '@ant-design/icons';

import AuthService from '../api/AuthService';
import { CreateUserBody } from '../api/models';

const SignUp = () => {
    const [messageApi, contextHolder] = message.useMessage();
    const [loading, setLoading] = useState(false);

    const onFinish = async (createUserForm: CreateUserBody) => {
        setLoading(true);

        await AuthService.register(createUserForm)
            .then(() => {
                messageApi.success('Вы успешно зарегистрировались');

                setTimeout(() => {
                    window.location.href = '/dashboard/profile';
                }, 100);
            })
            .catch(() => {
                messageApi.error('Ошибка регистрации');
            })
            .finally(() => setLoading(false));
    };

    return (
        <>
            {contextHolder}
            <Row className='auth'>
                <Col span={6} xs={{ span: 20 }} lg={{ span: 6 }}>
                    <Form
                        style={{ marginTop: 50 }}
                        name='signup'
                        initialValues={{
                            remember: true,
                        }}
                        onFinish={onFinish}
                    >
                        <Form.Item
                            name='username'
                            rules={[
                                {
                                    required: true,
                                    message: 'Пожалуйста, введите имя пользователя',
                                },
                                {
                                    validator: (_, value) => {
                                        const words = value?.trim().split(/\s+/);
                                        if (words && words.length === 3) {
                                            return Promise.resolve();
                                        }
                                        return Promise.reject(
                                            'Имя пользователя должно содержать 3 слова'
                                        );
                                    },
                                },
                            ]}
                        >
                            <Input
                                size='large'
                                prefix={<UserOutlined className='site-form-item-icon' />}
                                placeholder='Имя пользователя'
                            />
                        </Form.Item>
                        <Form.Item
                            name='email'
                            rules={[
                                {
                                    required: true,
                                    pattern: new RegExp(/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/),
                                    message: 'Пожалуйста, введите email',
                                },
                            ]}
                        >
                            <Input
                                size='large'
                                prefix={<MailOutlined className='site-form-item-icon' />}
                                placeholder='Email'
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
                                placeholder='Придумайте пароль'
                            />
                        </Form.Item>
                        <Form.Item>
                            <Form.Item valuePropName='checked' noStyle>
                                <Checkbox>Запомнить меня</Checkbox>
                            </Form.Item>

                            <Link to={'/login'}>Уже есть аккаунт</Link>
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
                                Зарегистрироваться
                            </Button>
                        </Form.Item>
                    </Form>
                </Col>
            </Row>
        </>
    );
};

export default SignUp;
