import { useEffect, useState } from 'react';
import { Anomaly } from '../api/models';
// eslint-disable-next-line
// @ts-ignore
import gifshot from 'gifshot';
import { Col, Divider, Row } from 'antd';

type Props = {
    anomaly: Anomaly;
};

const AnomalyCard = ({ anomaly }: Props) => {
    const [gifURL, setGifURL] = useState<string | null>(null);

    useEffect(() => {
        const generateGif = () => {
            gifshot.createGIF(
                {
                    images: anomaly.link.filter((_, i) => i % 5 === 0),
                    interval: 0.2, // Adjust interval as needed
                    numFrames: anomaly.link.length,
                    gifWidth: 400, // Adjust width as needed
                    gifHeight: 300, // Adjust height as needed
                    frameDuration: 1, // Adjust duration as needed
                },
                (obj: { image: string; error?: unknown }) => {
                    if (obj.error) {
                        console.error('Error creating GIF:', obj.error);
                    } else {
                        setGifURL(obj.image);
                    }
                }
            );
        };

        generateGif();

        // Cleanup
        return () => {
            setGifURL(null);
        };
    }, [anomaly.link]);

    return (
        <div>
            {anomaly.link.length > 0 && (
                <img style={{ width: '100%' }} src={anomaly.link[0]} alt='anomaly' />
            )}

            <Divider style={{ marginTop: 20, marginBottom: 20 }} />

            <Row justify={'center'}>
                <Col>{gifURL && <img src={gifURL} alt='Generated GIF' />}</Col>
            </Row>
        </div>
    );
};

export default AnomalyCard;
