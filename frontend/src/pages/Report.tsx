import { Breadcrumb, Card, Col, Layout, Row, Statistic, Typography } from 'antd';
import { Content } from 'antd/es/layout/layout';
import HeaderLayout from '../components/HeaderLayout';

const Report = () => {
    return (
        <Layout>
            <HeaderLayout />

            <Content className='site-layout' style={{ padding: '0 15px' }}>
                <Breadcrumb style={{ margin: '16px 0' }}>
                    <Breadcrumb.Item>Отчет</Breadcrumb.Item>
                </Breadcrumb>
                <div
                    className='content'
                    style={{ padding: 24, minHeight: 380, background: '#ffffff' }}
                >
                    <Typography.Title level={2}>Отчет</Typography.Title>

                    <Row gutter={16}>
                        <Col span={3}>
                            <Card bordered={false}>
                                <Statistic
                                    title='Обработано файлов'
                                    value={1}
                                    precision={0}
                                    valueStyle={{ color: '#3f8600' }}
                                />
                            </Card>
                        </Col>
                        <Col span={3}>
                            <Card bordered={false}>
                                <Statistic
                                    title='Всего файлов'
                                    value={1}
                                    precision={0}
                                    valueStyle={{ color: '#3f8600' }}
                                />
                            </Card>
                        </Col>
                    </Row>

                    {/* <Row className='report__files' gutter={16}>
                        <Col span={6}>
                            <Anomalies anomalies={[]} />
                        </Col>
                        <Col span={18}>
                            <Collapse
                                defaultActiveKey={['1']}
                                expandIconPosition={'start'}
                                items={getItems()}
                            />
                        </Col>
                    </Row> */}
                </div>
            </Content>
        </Layout>
    );
};

export default Report;
