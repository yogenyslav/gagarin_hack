import { Divider, Layout, Typography } from 'antd';
import { Content } from 'antd/es/layout/layout';
import HeaderLayout from '../components/HeaderLayout';
import { observer } from 'mobx-react-lite';
import { useParams } from 'react-router-dom';
import Report from '../components/Report';

const ReportPage = observer(() => {
    const { reportIdsWithComma } = useParams();

    const reportIds = reportIdsWithComma?.split(',');

    return (
        <>
            <Layout>
                <HeaderLayout />

                <Content className='site-layout' style={{ padding: '0 15px', marginTop: 15 }}>
                    <div
                        className='content'
                        style={{ padding: 24, minHeight: 380, background: '#ffffff' }}
                    >
                        <Typography.Title level={2}>Отчет</Typography.Title>

                        {reportIds &&
                            reportIds.map((reportId) => (
                                <>
                                    <Divider
                                        key={reportId}
                                        style={{ marginTop: 50, marginBottom: 20 }}
                                    />

                                    <Report key={reportId} reportId={+reportId} />
                                </>
                            ))}
                    </div>
                </Content>
            </Layout>
        </>
    );
});

export default ReportPage;
