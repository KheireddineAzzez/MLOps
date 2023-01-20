# Steps to produce this solution
## _MLOPS PROJECT 2022-2023_


### Purpose of this project

>Learn how to utilize Google Cloud to build a real-world machine learning pipeline, using the same techniques employed in large-scale projects.

## Requirements 
-  Linux distribution system (Ubuntu..) or you can use **WSL** if you have Microsoft Windows
-  Python 
-  TFX library 
-  Google clould Console
-  Docker 
-  Google Cloud Platform(GCP) Account
- Code Editor 

## Steps

### Prepare the Environment
#### Create GCP Project
- The first step is to install Docker on your pc because we are gonna to use docker to push our Docker image on google cloud registry. [Docker Instalation](https://docs.docker.com/engine/install/)
- The next step is one of the most important step in this  tutorial where we are going to create a [GCP](https://cloud.google.com/) Account.
  After creation you  GCP Account, we have to do some steps:
  - First of all we have to create a project, go now and click on that box ![](https://drive.google.com/u/0/uc?id=1xilD072rqAb-onjDaDe37J86VT3iPpJI&export=view) 
  - After clicking on that box, a popup will appear like this one , click on "New Project"
  ![](https://drive.google.com/u/0/uc?id=1hK0nTDkYBfjoj_QmSyekCnNofAhzN5RD&export=View)
  - After clicking on that project a new window will be open to put the data of you project in this situation you have only to put the name of you project like this:

   ![image](Tutorialimages/new_Project_form_forms.png)

   > Note : **we have complete now the creation of the project**

*** 

#### Activate services 

* In this step we are going to activate some service which are :
   - Google Cloud Registry (GCR)
   - Google cloud Storage
   - AI Platform 
   - Kubernets Engine

##### Google cloud Registry
> Google Cloud Registry (GCR) is a fully-managed, private Docker container registry that allows you to store, manage, and deploy Docker container images on Google Cloud Platform.

>To activate Google Cloud Registry (GCR) on Google Cloud Platform (GCP), you can follow these steps:

 **1.** Go to the GCP Console (console.cloud.google.com) and navigate to the Kubernetes Engine page.
 **2.** Select the project that you want to use for GCR.
 **3.** In the left sidebar, click on "Container Registry" to access the GCR page.
 
 **4.** On the GCR page, click on "Enable" to activate the service.



##### Google cloud Kubernets 
So now we are going to create Kubernets cluster for our pipeline :
To create a Kubernetes cluster on Google Cloud Platform (GCP), you can use the Google Kubernetes Engine (GKE) service. Here are the general steps to create a cluster:

**1.** Go to the GCP Console (console.cloud.google.com) and navigate to the Kubernetes Engine page.

**2.** Select the project that you want to use for the cluster.

**3.** Click on the "Create Cluster" button.

<img src="Tutorialimages/Kubernets_cluster.png"  height="200" width="400" />

***

**4.** After that  a pop up will appear. Choose the configure option for low cost

<img src="Tutorialimages/Choose_the_configure_option.png"  width="400" height="200">

**5.** On the "Create a Kubernetes cluster" page, you will have several options to configure the cluster.
  - For this part of configuration we are not gonna do any thing,but you can give a name to you cluster if you want
  
<img src="Tutorialimages/Cluster_basic.png"  width="600" height="300">

*** 

 **6.** Now go `Default pool` section make sure that there is at least 3 nodes :
  
  
<img src="Tutorialimages/Default%20pool.png"  width="500" height="300">

*** 
**7.** Now go to `Nodes` section where we are going to configure our nodes 
   - Make sure that you select **Ubuntu** as image for our node
   - The serie : **N1**
   - **Machine Type :** n1-standart-2(2 vCPu, 7.5GB memory) for low cost of money and it is enought for this project



<img src="Tutorialimages/Node%20Configuration.png"  width="500" height="300">

***
**8.** Now go to `Security ` section where we are going to give the access to ower nodes to use the other google API Service:
   
<img src="Tutorialimages/security_Section.png"  width="500" height="300">

> **Note**: After that, click on create 'This operation cloud take some time'

***

**9.** After the creation go back to the [Kubernets lists](https://console.cloud.google.com/kubernetes/list) you must see your cluster runing : 

<img src="Tutorialimages/cluster_running.png"  width="600" >


### Install Google Cloud SDK
> The Google Cloud SDK is a set of tools for interacting with Google Cloud services through the command line

Download the Google Cloud SDK installer for your operating system from this link: [Google SDK Download](https://cloud.google.com/sdk/docs/install)

Run the installer and follow the prompts. This will install the gcloud command-line tool and other components of the SDK.

After installation, open a command prompt or terminal window and run the command gcloud init to initialize the SDK and set up your Google Cloud project.

If prompted, log in to your Google account (choose the google account that you create with you GCP Acount) and select the project you want to use with the SDK.

***
### Google Cloud AI Platform
- Now go to Goolge cloud [AI Platform](https://console.cloud.google.com/ai-platform) to create Kubeflow instance


<img src="Tutorialimages/Google_Cloud_Piple_AI_Platform.png"  width="600" />

***
- Now a new window appeared, click on create New instance

<img src="Tutorialimages/Click_on_create_new_Instance_Kubeflow.png"  width="600" />

***

- Now a new window appeared, click on configure because we are going to configure the kubeflow depends on the nodes that we have been created previousily in [Kubernetes](#google-cloud-kubernets) section

<img src="Tutorialimages/Configure_KubeFlow.png"  width="600" />

  ***

- After clicking on  the Configure option button, a new window will appear, for this configuation we are gonna to choose the cluster that we are going to run our KubeFlow on, for that reason we will choose the cluster [Kubernetes](#google-cloud-kubernets) that we created in the previous steps. And then click on Deploy

<img src="Tutorialimages/Final_Step_of_kubeFlow.png"  height="400" />
 
> **Note**: This operation cloud take some time
***

- Now you can access to your KubeFLow instance by clicking on Open Pipeline Dashboard

<img src="Tutorialimages/Results_of_KubeFlow)install.png"  height="400" />

***

- The dashboard will be something like this  
<br>
<img src="Tutorialimages/KubeFlow_Dashboard.png"  width="400" height="400" />

***

#### Get Access Token 
- To get access token to your Google cloud environment you have to go to [AIM and Admin](https://console.cloud.google.com/iam-admin) in order to get access token to used later with Goolge SDK

  **1.** First Step go to Service Account
  **2.** click on the action button that related to your project
  **3.** Click on message key

<img src="Tutorialimages/Token_Form_IAM_Admin.png"  width="600" height="400" />
<br/>

<br/>

**4.** After clicking on messages keys a window will appear, next click on create new key. After creating the key, download it and save it because we are goinng to need it later.

<img src="Tutorialimages/Click_one_Create_new_Key.png"  width="600" height="400" />

***

### Actions

#### Docker 
Now we are going to upload the image that would being use to create