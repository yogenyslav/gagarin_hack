import {
    Breadcrumb,
    Button,
    Col,
    Form,
    Input,
    Layout,
    Row,
    Segmented,
    Typography,
    Upload,
    message,
} from 'antd';
import { Content } from 'antd/es/layout/layout';
import { observer } from 'mobx-react-lite';
import { useState } from 'react';
import { UploadOutlined } from '@ant-design/icons';
import AnomalyApiServiceInstance from '../api/AnomalyApiService';
import HeaderLayout from '../components/HeaderLayout';

enum ExportType {
    UploadVideo = 'Загрузить видео',
    RTSP = 'Указать RTSP ссылку',
}

const Home = observer(() => {
    const [selectedExportType, setSelectedExportType] = useState<
        'Загрузить видео' | 'Указать RTSP ссылку'
    >('Загрузить видео');
    const [messageApi, contextHolder] = message.useMessage();
    const [form] = Form.useForm();
    const [loading, setLoading] = useState<boolean>(false);

    const uploadRTSPLink = () => {
        const { rtspLink } = form.getFieldsValue();

        if (!rtspLink) {
            messageApi.error('Введите RTSP ссылку');
            return;
        }

        setLoading(true);

        AnomalyApiServiceInstance.sendRTSPUrl(rtspLink)
            .then((data) => {
                messageApi.success('Начинается обработка файла');

                setTimeout(() => {
                    window.location.href = `/report/${data.id}`;
                }, 1000);
            })
            .catch(() => {
                messageApi.error('Ошибка загрузки ссылки. Попробуйте еще раз.');
            })
            .finally(() => {
                setLoading(false);
            });
    };

    return (
        <>
            {contextHolder}
            <Layout>
                <HeaderLayout />

                <Content className='site-layout' style={{ padding: '0 15px' }}>
                    <Breadcrumb style={{ margin: '16px 0' }}>
                        <Breadcrumb.Item>Загрузка видео/трансляции</Breadcrumb.Item>
                    </Breadcrumb>
                    <div
                        className='content'
                        style={{ padding: 24, minHeight: 380, background: '#ffffff' }}
                    >
                        <Typography.Title level={2}>Загрузка видео/трансляции</Typography.Title>

                        <Row>
                            <Col span={24}>
                                <Segmented
                                    options={['Загрузить видео', 'Указать RTSP ссылку']}
                                    onChange={(value) => setSelectedExportType(value as ExportType)}
                                    defaultChecked={true}
                                />
                            </Col>
                        </Row>

                        {selectedExportType === ExportType.UploadVideo && (
                            <Row style={{ marginTop: 20 }}>
                                <Col>
                                    <Upload
                                        name='file'
                                        beforeUpload={(file) => {
                                            setLoading(true);

                                            AnomalyApiServiceInstance.sendVideo(file)
                                                .then((data) => {
                                                    messageApi.success(
                                                        'Начинается обработка файла'
                                                    );

                                                    setTimeout(() => {
                                                        window.location.href = `/report/${data.id}`;
                                                    }, 1000);
                                                })
                                                .catch(() => {
                                                    messageApi.error(
                                                        'Ошибка загрузки файла. Попробуйте еще раз.'
                                                    );
                                                })
                                                .finally(() => {
                                                    setLoading(false);
                                                });

                                            return false;
                                        }}
                                        multiple={false}
                                        maxCount={1}
                                    >
                                        <Button icon={<UploadOutlined />}>Загрузить видео</Button>
                                    </Upload>
                                </Col>
                            </Row>
                        )}

                        {selectedExportType === ExportType.RTSP && (
                            <Row style={{ marginTop: 20 }}>
                                <Col span={24}>
                                    <Form layout={'vertical'} form={form}>
                                        <Form.Item
                                            name={'rtspLink'}
                                            style={{ width: '100%' }}
                                            label='RTSP ссылка'
                                        >
                                            <Input />
                                        </Form.Item>
                                        <Form.Item>
                                            <Button
                                                loading={loading}
                                                onClick={() => uploadRTSPLink()}
                                                type='primary'
                                            >
                                                Отправить
                                            </Button>
                                        </Form.Item>
                                    </Form>
                                </Col>
                            </Row>
                        )}
                    </div>
                </Content>
            </Layout>
        </>
    );
});

export default Home;
