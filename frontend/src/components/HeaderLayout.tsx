import { Layout, Menu, MenuProps } from 'antd';
import { Link } from 'react-router-dom';

const { Header } = Layout;

const items: MenuProps['items'] = [
    {
        key: '1',
        label: (
            <Link to='/home' style={{ color: 'white' }}>
                Загрузить видео
            </Link>
        ),
        style: {
            background: 'transparent',
        },
    },
];

const HeaderLayout = () => {
    return (
        <Header style={{ display: 'flex', alignItems: 'center' }}>
            <div className='demo-logo' />
            <Menu
                theme='dark'
                mode='horizontal'
                defaultSelectedKeys={['1']}
                items={items}
                style={{ flex: 1, minWidth: 0 }}
            />
        </Header>
    );
};

export default HeaderLayout;
