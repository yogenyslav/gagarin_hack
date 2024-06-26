import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';

import './index.scss';
import { ConfigProvider } from 'antd';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
    <ConfigProvider
        theme={{
            token: {
                colorPrimary: '#0277FF',
            },
        }}
    >
        <RouterProvider router={router} />
    </ConfigProvider>
);
