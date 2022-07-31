import json
import boto3
import datetime
import base64

ec2_client = boto3.client('ec2')
cw_client = boto3.client('cloudwatch')


def lambda_handler(event, context):
    # get current instance id
    ec2_instance_id = event['detail']['instance-id']

    # get current instance type
    get_instance_type = ec2_client.describe_instance_attribute(
        Attribute='instanceType',
        InstanceId=ec2_instance_id
    )

    print('describe_instance_attribute response =', get_instance_type)

    instance_type = get_instance_type['InstanceType']['Value']

    # specify the amount of vCPU based on the instance type
    if instance_type == 't3.nano':
        vcpu = 2
    elif instance_type == 't3.micro':
        vcpu = 2
    elif instance_type == 't3.small':
        vcpu = 2
    elif instance_type == 't3.medium':
        vcpu = 2
    elif instance_type == 't3.large':
        vcpu = 2
    elif instance_type == 't3.xlarge':
        vcpu = 4
    elif instance_type == 't3.2xlarge':
        vcpu = 8

    # get the last 1 minute of vCPU usage from CloudWatch
    get_vcpu_usage_data = cw_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'identifier',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': ec2_instance_id
                            }
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Maximum'
                }
            },
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(minutes=5),
        EndTime=datetime.datetime.now(),
    )

    print('get_metric_data response =', get_vcpu_usage_data)

    vcpu_usage_data = get_vcpu_usage_data['MetricDataResults'][0]['Values'][0]

    selection1(vcpu, vcpu_usage_data)

    return {
        'statusCode': 200,
        'body': json.dumps('An EC2 Spot Instance has been requested!')
    }

# ********** FUZZY SUGENO METHOD **********


def selection1(current, usage):  # current = the current amount of vCPU; usage = vCPU usage
    # ------STEP 1: FUZZIFICATION------
    # Current vCPU variable initiation
    if current == 2:
        value_2 = 1
        value_4 = 0
        value_8 = 0

    elif current == 4:
        value_2 = 0
        value_4 = 1
        value_8 = 0

    elif current == 8:
        value_2 = 0
        value_4 = 0
        value_8 = 1

    else:
        value_2 = 0
        value_4 = 0
        value_8 = 0

    # vCPU Usage variable initiation
    if usage <= 25:
        value_low = 1
        value_fair = 0
        value_high = 0

    elif usage > 25 and usage < 50:
        value_low = (50 - usage) / (50 - 25)
        value_fair = (usage - 25) / (50 - 25)
        value_high = 0

    elif usage == 50:
        value_low = 0
        value_fair = 1
        value_high = 0

    elif usage > 50 and usage < 75:
        value_low = 0
        value_fair = (75 - usage) / (75 - 50)
        value_high = (usage - 50) / (75 - 50)

    elif usage >= 75:
        value_low = 0
        value_fair = 0
        value_high = 1

    # ------STEP 2: INFERENCE------
    result = []

    # [R1] IF Current vCPU = 2 AND vCPU Usage = low,
    #      THEN vCPU Verdict = constant
    α1 = min(value_2, value_low)
    z1 = current
    result.append([α1, z1])

    # [R2] IF Current vCPU = 2 AND vCPU Usage = fair,
    #      THEN vCPU Verdict = constant
    α2 = min(value_2, value_fair)
    z2 = current
    result.append([2, z2])

    # [R3] IF Current vCPU = 2 AND vCPU Usage = high,
    #      THEN vCPU Verdict = higher
    α3 = min(value_2, value_high)
    z3 = current*2
    result.append([α3, z3])

    # [R4] IF Current vCPU = 4 AND vCPU Usage = low,
    #      THEN vCPU Verdict = lower
    α4 = min(value_4, value_low)
    z4 = current/2
    result.append([α4, z4])

    # [R5] IF Current vCPU = 4 AND vCPU Usage = fair,
    #      THEN vCPU Verdict = constant
    α5 = min(value_4, value_fair)
    z5 = current
    result.append([α5, z5])

    # [R6] IF Current vCPU = 4 AND vCPU Usage = high,
    #      THEN vCPU Verdict = higher
    α6 = min(value_4, value_high)
    z6 = current*2
    result.append([α6, z6])

    # [R7] IF Current vCPU = 8 AND vCPU Usage = low,
    #      THEN vCPU Verdict = lower
    α7 = min(value_8, value_low)
    z7 = current/2
    result.append([α7, z7])

    # [R8] IF Current vCPU = 8 AND vCPU Usage = fair,
    #      THEN vCPU Verdict = constant
    α8 = min(value_8, value_fair)
    z8 = current
    result.append([α8, z8])

    # [R9] IF Current vCPU = 8 AND vCPU Usage = high,
    #      THEN vCPU Verdict = constant
    α9 = min(value_8, value_high)
    z9 = current
    result.append([α9, z9])

    print("hasil tahap inferensi =", result)

    # ------STEP 3:  DEFFUZIFICATION------
    numerator_new = 0
    denominator_new = 0

    for n in range(0, 8):
        numerator = result[n][0]*result[n][1]
        denominator = result[n][0]

        numerator_new = numerator_new + numerator
        denominator_new = denominator_new + denominator

    z = numerator_new/denominator_new
    vcpu_count = current

    print("hasil z =", z)

    adjustment(z, vcpu_count)


def adjustment(z, vcpu_count):
    if vcpu_count == 2:
        if z - vcpu_count < 0:
            new_vcpu = 2
        elif z - vcpu_count == 0:
            new_vcpu = 2
        elif z - vcpu_count > 0:
            new_vcpu = 4

    elif vcpu_count == 4:
        if z - vcpu_count < 0:
            new_vcpu = 2
        elif z - vcpu_count == 0:
            new_vcpu = 4
        elif z - vcpu_count > 0:
            new_vcpu = 8

    elif vcpu_count == 8:
        if z - vcpu_count < 0:
            new_vcpu = 4
        elif z - vcpu_count == 0:
            new_vcpu = 8
        elif z - vcpu_count > 0:
            new_vcpu = 8

    if new_vcpu == 2:
        selection2()

    elif new_vcpu == 4:
        price_check_a = ec2_client.describe_spot_price_history(
            AvailabilityZone='ap-southeast-3a',
            EndTime=datetime.datetime.now(),
            InstanceTypes=['t3.xlarge'],
            MaxResults=1,
            StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
        )
        price_check_b = ec2_client.describe_spot_price_history(
            AvailabilityZone='ap-southeast-3b',
            EndTime=datetime.datetime.now(),
            InstanceTypes=['t3.xlarge'],
            MaxResults=1,
            StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
        )
        price_check_c = ec2_client.describe_spot_price_history(
            AvailabilityZone='ap-southeast-3c',
            EndTime=datetime.datetime.now(),
            InstanceTypes=['t3.xlarge'],
            MaxResults=1,
            StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
        )

        price_on_each_az = [float(price_check_a['SpotPriceHistory'][0]['SpotPrice']), float(
            price_check_b['SpotPriceHistory'][0]['SpotPrice']), float(price_check_c['SpotPriceHistory'][0]['SpotPrice'])]
        chosen_az = price_on_each_az.index(min(price_on_each_az))

        if chosen_az == 0:
            request('t3.xlarge', 'ap-southeast-3a', price_on_each_az[0])
        elif chosen_az == 1:
            request('t3.xlarge', 'ap-southeast-3b', price_on_each_az[1])
        elif chosen_az == 2:
            request('t3.xlarge', 'ap-southeast-3c', price_on_each_az[2])

    elif new_vcpu == 8:
        price_check_a = ec2_client.describe_spot_price_history(
            AvailabilityZone='ap-southeast-3a',
            EndTime=datetime.datetime.now(),
            InstanceTypes=['t3.2xlarge'],
            MaxResults=1,
            StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
        )
        price_check_b = ec2_client.describe_spot_price_history(
            AvailabilityZone='ap-southeast-3b',
            EndTime=datetime.datetime.now(),
            InstanceTypes=['t3.2xlarge'],
            MaxResults=1,
            StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
        )
        price_check_c = ec2_client.describe_spot_price_history(
            AvailabilityZone='ap-southeast-3c',
            EndTime=datetime.datetime.now(),
            InstanceTypes=['t3.2xlarge'],
            MaxResults=1,
            StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
        )
        price_on_each_az = [float(price_check_a['SpotPriceHistory'][0]['SpotPrice']), float(
            price_check_b['SpotPriceHistory'][0]['SpotPrice']), float(price_check_c['SpotPriceHistory'][0]['SpotPrice'])]
        chosen_az = price_on_each_az.index(min(price_on_each_az))

        if chosen_az == 0:
            request('t3.2xlarge', 'ap-southeast-3a', price_on_each_az[0])
        elif chosen_az == 1:
            request('t3.2xlarge', 'ap-southeast-3b', price_on_each_az[1])
        elif chosen_az == 2:
            request('t3.2xlarge', 'ap-southeast-3c', price_on_each_az[2])

    print('jumlah vCPU baru =', new_vcpu)

# ********** BEST-WORST METHOD **********


def selection2():
    # initiate optimal weights on each criteria
    memory_weight = 0.74
    price_weight = 0.18
    discount_weight = 0.08

    # initiate all possible alternatives
    alt1 = {'az': 'ap-southeast-3a',
            'discount(%)': 0,
            'instance_type': 't3.nano',
            'price': 0
            }
    alt2 = {'az': 'ap-southeast-3b',
            'discount(%)': 0,
            'instance_type': 't3.nano',
            'price': 0
            }
    alt3 = {'az': 'ap-southeast-3c',
            'discount(%)': 0,
            'instance_type': 't3.nano',
            'price': 0
            }
    alt4 = {'az': 'ap-southeast-3a',
            'discount(%)': 0,
            'instance_type': 't3.micro',
            'price': 0
            }
    alt5 = {'az': 'ap-southeast-3b',
            'discount(%)': 0,
            'instance_type': 't3.micro',
            'price': 0
            }
    alt6 = {'az': 'ap-southeast-3c',
            'discount(%)': 0,
            'instance_type': 't3.micro',
            'price': 0
            }
    alt7 = {'az': 'ap-southeast-3a',
            'discount(%)': 0,
            'instance_type': 't3.small',
            'price': 0
            }
    alt8 = {'az': 'ap-southeast-3b',
            'discount(%)': 0,
            'instance_type': 't3.small',
            'price': 0
            }
    alt9 = {'az': 'ap-southeast-3c',
            'discount(%)': 0,
            'instance_type': 't3.small',
            'price': 0
            }
    alt10 = {'az': 'ap-southeast-3a',
             'discount(%)': 0,
             'instance_type': 't3.medium',
             'price': 0
             }
    alt11 = {'az': 'ap-southeast-3b',
             'discount(%)': 0,
             'instance_type': 't3.medium',
             'price': 0
             }
    alt12 = {'az': 'ap-southeast-3c',
             'discount(%)': 0,
             'instance_type': 't3.medium',
             'price': 0
             }
    alt13 = {'az': 'ap-southeast-3a',
             'discount(%)': 0,
             'instance_type': 't3.large',
             'price': 0
             }
    alt14 = {'az': 'ap-southeast-3b',
             'discount(%)': 0,
             'instance_type': 't3.large',
             'price': 0
             }
    alt15 = {'az': 'ap-southeast-3c',
             'discount(%)': 0,
             'instance_type': 't3.large',
             'price': 0
             }

    # get the current Spot Instance price
    spot_price_1 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt1['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt1['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_2 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt2['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt2['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_3 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt3['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt3['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_4 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt4['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt4['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_5 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt5['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt5['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_6 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt6['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt6['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_7 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt7['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt7['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_8 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt8['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt8['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_9 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt9['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt9['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_10 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt10['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt10['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_11 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt11['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt11['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_12 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt12['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt12['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_13 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt13['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt13['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_14 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt14['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt14['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    spot_price_15 = ec2_client.describe_spot_price_history(
        AvailabilityZone=alt15['az'],
        EndTime=datetime.datetime.now(),
        InstanceTypes=[alt15['instance_type']],
        MaxResults=1,
        ProductDescriptions=[
            'Linux/UNIX'
        ],
        StartTime=datetime.datetime.now()-datetime.timedelta(days=1)
    )

    # assign new current value
    alt1['discount(%)'] = (
        0.0066 - float(spot_price_1['SpotPriceHistory'][0]['SpotPrice'])) / 0.0066 * 100
    alt1['price'] = float(spot_price_1['SpotPriceHistory'][0]['SpotPrice'])
    alt2['discount(%)'] = (
        0.0066 - float(spot_price_2['SpotPriceHistory'][0]['SpotPrice'])) / 0.0066 * 100
    alt2['price'] = float(spot_price_2['SpotPriceHistory'][0]['SpotPrice'])
    alt3['discount(%)'] = (
        0.0066 - float(spot_price_3['SpotPriceHistory'][0]['SpotPrice'])) / 0.0066 * 100
    alt3['price'] = float(spot_price_3['SpotPriceHistory'][0]['SpotPrice'])
    alt4['discount(%)'] = (
        0.0123 - float(spot_price_4['SpotPriceHistory'][0]['SpotPrice'])) / 0.0123 * 100
    alt4['price'] = float(spot_price_4['SpotPriceHistory'][0]['SpotPrice'])
    alt5['discount(%)'] = (
        0.0123 - float(spot_price_5['SpotPriceHistory'][0]['SpotPrice'])) / 0.0123 * 100
    alt5['price'] = float(spot_price_5['SpotPriceHistory'][0]['SpotPrice'])
    alt6['discount(%)'] = (
        0.0123 - float(spot_price_6['SpotPriceHistory'][0]['SpotPrice'])) / 0.0123 * 100
    alt6['price'] = float(spot_price_6['SpotPriceHistory'][0]['SpotPrice'])
    alt7['discount(%)'] = (
        0.0264 - float(spot_price_7['SpotPriceHistory'][0]['SpotPrice'])) / 0.0264 * 100
    alt7['price'] = float(spot_price_7['SpotPriceHistory'][0]['SpotPrice'])
    alt8['discount(%)'] = (
        0.0264 - float(spot_price_8['SpotPriceHistory'][0]['SpotPrice'])) / 0.0264 * 100
    alt8['price'] = float(spot_price_8['SpotPriceHistory'][0]['SpotPrice'])
    alt9['discount(%)'] = (
        0.0264 - float(spot_price_9['SpotPriceHistory'][0]['SpotPrice'])) / 0.0264 * 100
    alt9['price'] = float(spot_price_9['SpotPriceHistory'][0]['SpotPrice'])
    alt10['discount(%)'] = (
        0.0528 - float(spot_price_10['SpotPriceHistory'][0]['SpotPrice'])) / 0.0528 * 100
    alt10['price'] = float(spot_price_10['SpotPriceHistory'][0]['SpotPrice'])
    alt11['discount(%)'] = (
        0.0528 - float(spot_price_11['SpotPriceHistory'][0]['SpotPrice'])) / 0.0528 * 100
    alt11['price'] = float(spot_price_11['SpotPriceHistory'][0]['SpotPrice'])
    alt12['discount(%)'] = (
        0.0528 - float(spot_price_12['SpotPriceHistory'][0]['SpotPrice'])) / 0.0528 * 100
    alt12['price'] = float(spot_price_12['SpotPriceHistory'][0]['SpotPrice'])
    alt13['discount(%)'] = (
        0.1056 - float(spot_price_13['SpotPriceHistory'][0]['SpotPrice'])) / 0.1056 * 100
    alt13['price'] = float(spot_price_13['SpotPriceHistory'][0]['SpotPrice'])
    alt14['discount(%)'] = (
        0.1056 - float(spot_price_14['SpotPriceHistory'][0]['SpotPrice'])) / 0.1056 * 100
    alt14['price'] = float(spot_price_14['SpotPriceHistory'][0]['SpotPrice'])
    alt15['discount(%)'] = (
        0.1056 - float(spot_price_15['SpotPriceHistory'][0]['SpotPrice'])) / 0.1056 * 100
    alt15['price'] = float(spot_price_15['SpotPriceHistory'][0]['SpotPrice'])

    # normalization
    array_memory = [0.5, 0.5, 0.5, 1, 1, 1, 2, 2, 2, 4, 4, 4, 8, 8, 8]
    array_price = []
    array_discount = []

    array_price.extend([alt1['price'], alt2['price'], alt3['price'], alt4['price'], alt5['price'], alt6['price'], alt7['price'],
                       alt8['price'], alt9['price'], alt10['price'], alt11['price'], alt12['price'], alt13['price'], alt14['price'], alt15['price']])
    array_discount.extend([alt1['discount(%)'], alt2['discount(%)'], alt3['discount(%)'], alt4['discount(%)'], alt5['discount(%)'], alt6['discount(%)'], alt7['discount(%)'],
                          alt8['discount(%)'], alt9['discount(%)'], alt10['discount(%)'], alt11['discount(%)'], alt12['discount(%)'], alt13['discount(%)'], alt14['discount(%)'], alt15['discount(%)']])

    array_memory_new = [0.625, 0.625, 0.625, 0.125, 0.125,
                        0, 125, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 1, 1, 1]
    array_price_new = []
    array_discount_new = []

    max_price = max(array_price)
    max_discount = max(array_discount)

    array_price_new.extend([1 - (array_price[0] / max_price), 1 - (array_price[1] / max_price), 1 - (array_price[2] / max_price), 1 - (array_price[3] / max_price), 1 - (array_price[4] / max_price), 1 - (array_price[5] / max_price), 1 - (array_price[6] / max_price), 1 - (
        array_price[7] / max_price), 1 - (array_price[8] / max_price), 1 - (array_price[9] / max_price), 1 - (array_price[10] / max_price), 1 - (array_price[11] / max_price), 1 - (array_price[12] / max_price), 1 - (array_price[13] / max_price), 1 - (array_price[14] / max_price)])
    array_discount_new.extend([array_discount[0] / max_discount, array_discount[1] / max_discount, array_discount[2] / max_discount, array_discount[3] / max_discount, array_discount[4] / max_discount, array_discount[5] / max_discount, array_discount[6] / max_discount,
                              array_discount[7] / max_discount, array_discount[8] / max_discount, array_discount[9] / max_discount, array_discount[10] / max_discount, array_discount[11] / max_discount, array_discount[12] / max_discount, array_discount[13] / max_discount, array_discount[14] / max_discount])

    performance_matrix = []
    performance_matrix.extend(
        [array_memory_new, array_price_new, array_discount_new])

    # calculate overall values to find the best alternative
    overall_values = []

    for a in range(0, 14):
        memory_value = performance_matrix[0][a] * memory_weight
        price_value = performance_matrix[1][a] * price_weight
        discount_value = performance_matrix[2][a] * discount_weight

        alternative_value = memory_value + price_value + discount_value

        overall_values.append(alternative_value)

    final_decision = overall_values.index(max(overall_values))

    if final_decision == 0:
        instance_data = alt1
    elif final_decision == 1:
        instance_data = alt2
    elif final_decision == 2:
        instance_data = alt3
    elif final_decision == 3:
        instance_data = alt4
    elif final_decision == 4:
        instance_data = alt5
    elif final_decision == 5:
        instance_data = alt6
    elif final_decision == 6:
        instance_data = alt7
    elif final_decision == 7:
        instance_data = alt8
    elif final_decision == 8:
        instance_data = alt9
    elif final_decision == 9:
        instance_data = alt10
    elif final_decision == 10:
        instance_data = alt11
    elif final_decision == 11:
        instance_data = alt12
    elif final_decision == 12:
        instance_data = alt13
    elif final_decision == 13:
        instance_data = alt14
    elif final_decision == 14:
        instance_data = alt15

    print('instance_specs = ', instance_data)
    request(instance_data['instance_type'],
            instance_data['az'], instance_data['price'])


def request(instanceType, az, price):
    price_str = str(price)

    user_data = '''#!/bin/bash
                sudo apt-get update
                sudo apt-get -y install stress-ng
                sudo apt-get install cron
                sudo -i
                echo "0 * * * * root stress-ng --cpu 80 --timeout 10m" >> /etc/cron.d/stressor
                echo "10 * * * * root stress-ng --cpu 20 --timeout 10m" >> /etc/cron.d/stressor
                echo "20 * * * * root stress-ng --cpu 120 --timeout 10m" >> /etc/cron.d/stressor
                echo "30 * * * * root stress-ng --cpu 30 --timeout 10m" >> /etc/cron.d/stressor
                echo "40 * * * * root stress-ng --cpu 200 --timeout 10m" >> /etc/cron.d/stressor
                echo "50 * * * * root stress-ng --cpu 10 --timeout 10m" >> /etc/cron.d/stressor'''

    encoded_user_data = (base64.b64encode(user_data.encode())).decode("utf-8")

    spot_request = ec2_client.request_spot_instances(
        InstanceCount=1,
        LaunchSpecification={
            'ImageId': 'ami-0c1460efd8855de7c',
            'InstanceType': instanceType,
            'Monitoring': {
                'Enabled': True
            },
            'Placement': {
                'AvailabilityZone': az,
            },
            'UserData': encoded_user_data
        },
        SpotPrice=price_str,
        Type='one-time',
        TagSpecifications=[
            {
                'ResourceType': 'spot-instances-request',
                'Tags': [
                    {
                        'Key': 'usage',
                        'Value': 'experiment'
                    },
                ]
            },
        ],
        InstanceInterruptionBehavior='terminate'
    )

    print('request_spot_instances response =', spot_request)
