import {
    Button,
    Col,
    Form,
    Input,
    Layout,
    Radio,
    RadioChangeEvent,
    Row,
    Segmented,
    Spin,
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
import { ModelType } from '../api/constants';

enum ExportType {
    UploadVideo = 'Загрузить видео',
    RTSP = 'Указать RTSP ссылку',
    UploadArchive = 'Загрузить архив',
}

const Home = observer(() => {
    const [selectedExportType, setSelectedExportType] = useState<
        'Загрузить видео' | 'Указать RTSP ссылку' | 'Загрузить архив'
    >('Загрузить видео');
    const [messageApi, contextHolder] = message.useMessage();
    const [form] = Form.useForm();
    const [loading, setLoading] = useState<boolean>(false);
    const [modelType, setModelType] = useState(ModelType.RGB);

    const onChange = (e: RadioChangeEvent) => {
        console.log('radio checked', e.target.value);
        setModelType(e.target.value);
    };

    const uploadRTSPLink = () => {
        const { rtspLink } = form.getFieldsValue();

        if (!rtspLink) {
            messageApi.error('Введите RTSP ссылку');
            return;
        }

        setLoading(true);

        AnomalyApiServiceInstance.sendRTSPUrl(rtspLink, modelType)
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

                <Content className='site-layout' style={{ padding: '0 15px', marginTop: 15 }}>
                    <div
                        className='content'
                        style={{ padding: 24, minHeight: 380, background: '#ffffff' }}
                    >
                        <Typography.Title level={2}>Загрузка видео/трансляции</Typography.Title>

                        <Row>
                            <Col span={24}>
                                <Segmented
                                    options={[
                                        'Загрузить видео',
                                        'Указать RTSP ссылку',
                                        'Загрузить архив',
                                    ]}
                                    onChange={(value) => setSelectedExportType(value as ExportType)}
                                    defaultChecked={true}
                                />
                            </Col>
                        </Row>

                        <Row style={{ marginTop: 20 }}>
                            <Col>
                                <Radio.Group onChange={onChange} value={modelType}>
                                    <Radio value={ModelType.BYTES}>Анализ байтового потока</Radio>
                                    <Radio value={ModelType.RGB}>Анализ в формате RGB</Radio>
                                </Radio.Group>
                            </Col>
                        </Row>

                        {selectedExportType === ExportType.UploadVideo && (
                            <Row gutter={[16, 16]} align={'middle'} style={{ marginTop: 20 }}>
                                <Col>{loading && <Spin />}</Col>
                                <Col>
                                    <Upload
                                        disabled={loading}
                                        name='file'
                                        beforeUpload={(file) => {
                                            setLoading(true);

                                            AnomalyApiServiceInstance.sendVideo(file, modelType)
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

                        {selectedExportType === ExportType.UploadArchive && (
                            <Row gutter={[16, 16]} align={'middle'} style={{ marginTop: 20 }}>
                                <Col>{loading && <Spin />}</Col>
                                <Col>
                                    <Upload
                                        disabled={loading}
                                        name='file'
                                        beforeUpload={(file) => {
                                            setLoading(true);

                                            AnomalyApiServiceInstance.sendArchive(file, modelType)
                                                .then((data) => {
                                                    messageApi.success(
                                                        'Начинается обработка файла'
                                                    );

                                                    console.log(data);

                                                    setTimeout(() => {
                                                        window.location.href = `/report/${data.ids.join(
                                                            ','
                                                        )}`;
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
                                        <Button icon={<UploadOutlined />}>Загрузить архив</Button>
                                    </Upload>
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
