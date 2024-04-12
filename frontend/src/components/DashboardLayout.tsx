import { Avatar, Col, Layout, Menu, theme, Typography } from 'antd';
import React from 'react';
import { Link, Outlet } from 'react-router-dom';

import { DashboardOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';

import type { MenuProps } from 'antd';
import AuthService from '../api/AuthService';
const { Header, Content, Sider } = Layout;

const menuItems: MenuProps['items'] = [
    {
        label: <Link to='/team'>Команда</Link>,
        icon: React.createElement(DashboardOutlined),
        key: 'team',
    },
];

const DashboardLayout: React.FC = () => {
    const {
        token: { colorBgContainer },
    } = theme.useToken();

    return (
        <Layout className='dashboard-layout'>
            <Header className='header'>
                <Typography.Title level={3} className='logo'>
                    MISIS
                </Typography.Title>

                <Col>
                    <Avatar style={{ backgroundColor: '#666' }} icon={<UserOutlined />} />

                    <span style={{ marginLeft: 10, color: '#fff' }}>
                        {`${
                            AuthService.getCurrentUser()?.user?.name ??
                            AuthService.getCurrentUser()?.user.name
                        }`}
                    </span>

                    <Link
                        onClick={() => {
                            AuthService.logout();

                            setTimeout(() => {
                                window.location.href = '/login';
                            }, 100);
                        }}
                        to='/login'
                        style={{ marginLeft: 20 }}
                    >
                        <LogoutOutlined style={{ color: '#fff' }} />
                    </Link>
                </Col>
            </Header>
            <Layout>
                <Sider width={200} style={{ background: colorBgContainer }}>
                    <Menu
                        mode='inline'
                        defaultSelectedKeys={['profile']}
                        defaultOpenKeys={['profile']}
                        style={{ height: '100%', borderRight: 0 }}
                        items={menuItems}
                    />
                </Sider>
                <Layout style={{ padding: '24px 24px 24px' }}>
                    <Content
                        style={{
                            padding: 24,
                            margin: 0,
                            minHeight: 280,
                            background: colorBgContainer,
                        }}
                    >
                        <Outlet />
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    );
};

export default DashboardLayout;
